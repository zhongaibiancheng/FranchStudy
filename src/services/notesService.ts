// src/services/notesService.js
import lesson1Notes from "@/data/lesson_01/lesson1_notes";
import lesson3Notes from "@/data/lesson_03/lesson3_notes";

export type LevelKey = "A" | "B" | "C";

export type MemorizeItem = {
  fr: string;
  zh: string;
};

export type Drill = any;

export type GrammarPoint = {
  id: string;
  name_zh: string;
  name_fr: string;
  mini_rule: string;
  must_memorize: MemorizeItem[];
  drills?: Drill[];
};

export type RootData = {
  source_title: string;
  levels: Record<LevelKey, GrammarPoint[]>;
};


/**
 * 未来扩展：
 * import lesson4Notes from "@/data/lesson4_notes";
 * 然后加进 NOTES_MAP
 */
const NOTES_MAP = {
  1:lesson1Notes,
  3: lesson3Notes
};

/**
 * @param {number} lessonNo
 * @returns {object} RootData-like
 */
export default function getNotesDataByLesson(lessonNo) {
  return NOTES_MAP[lessonNo] ?? NOTES_MAP[3];
}
