// LessonService.js
import lesson_01_01 from "@/data/lesson_01/lesson_01_01.json";
import lesson_01_02 from "@/data/lesson_01/lesson_01_02.json";

import lesson_03_01 from "@/data/lesson_03/lesson_03_01.json";
import lesson_03_02 from "@/data/lesson_03/lesson_03_02.json";


const lessonDatas = {
  '1_1': lesson_01_01,
  '1_2': lesson_01_02,
  '3_1': lesson_03_01,
  '3_2': lesson_03_02,
}
const options = {
  1:[{
    id:1,
    value:'对话',
    label:'对话'
  },
  {
    id:2,
    value:'文章1',
    label:'文章1'
  }],
  3:[
    {
    id:1,
    value:'对话',
    label:'对话'
  },
  {
    id:2,
    value:'文章1',
    label:'文章1'
  },
  ]
}


// 小工具函数：根据课号拿到对应的 wordData
function getLessonDataByLesson(lesson,part=1) {
  const data = lessonDatas[lesson+"_"+part]

  if (!data) {
    console.warn('[LessonService] 未找到该课号的数据，lesson =', lesson)
    return {}        // 返回空对象，避免报错
  }
  const option = options[lesson]

  return {
    'data':data,
    'option':option
  }
}

export default getLessonDataByLesson
