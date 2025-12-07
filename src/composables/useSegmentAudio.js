import { ref, watch, onBeforeUnmount } from 'vue'

export function useSegmentAudio(getLessonSrc) {
  const audio = new Audio()
  audio.preload = 'auto'

  const playingId = ref(null)
  let rafId = 0

  const setSrcIfNeeded = (src) => {
    if (!src) return
    // 统一成绝对地址对比，避免重复 set src
    const abs = new URL(src, window.location.origin).href
    if (audio.src !== abs) {
      audio.src = src
    }
  }

  const stop = () => {
    if (rafId) cancelAnimationFrame(rafId)
    rafId = 0
    audio.pause()
    playingId.value = null
  }

  const playSegment = (item, fallbackSrc) => {
    const start =
      item?.audio_start ??
      item?.audio?.start

    const end =
      item?.audio_end ??
      item?.audio?.end

    const src =
      item?.audio_src ??
      item?.audio?.src ??
      fallbackSrc ??
      (typeof getLessonSrc === 'function' ? getLessonSrc() : null)

    if (start == null || end == null || !src) {
      console.warn('[audio] missing start/end/src for', item?.id)
      return
    }

    const safeStart = Math.max(0, Number(start))
    const safeEnd = Math.max(safeStart, Number(end))

    setSrcIfNeeded(src)

    if (rafId) cancelAnimationFrame(rafId)
    rafId = 0

    audio.currentTime = safeStart
    playingId.value = item.id

    audio.play().catch((e) => {
      console.warn('[audio] play blocked', e)
      playingId.value = null
    })

    const tick = () => {
      if (!playingId.value) return
      // 给一点点容差，避免浮点误差
      if (audio.currentTime >= safeEnd - 0.03) {
        audio.pause()
        audio.currentTime = safeEnd
        playingId.value = null
        return
      }
      rafId = requestAnimationFrame(tick)
    }

    rafId = requestAnimationFrame(tick)
  }

  // 切课时自动换源
  watch(
    () => (typeof getLessonSrc === 'function' ? getLessonSrc() : null),
    (src) => {
      if (src) setSrcIfNeeded(src)
      stop()
    }
  )

  onBeforeUnmount(() => {
    stop()
    audio.src = ''
  })

  return { audio, playingId, playSegment, stop }
}
