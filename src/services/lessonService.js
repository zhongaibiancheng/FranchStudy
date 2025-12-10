// LessonService.js
import lesson_01_01 from "@/data/lesson_01/lesson_01_01.json";
import lesson_01_02 from "@/data/lesson_01/lesson_01_02.json";

import lesson_02_01 from "@/data/lesson_02/lesson_02_01.json";
import lesson_02_02 from "@/data/lesson_02/lesson_02_02.json";

import lesson_03_01 from "@/data/lesson_03/lesson_03_01.json";
import lesson_03_02 from "@/data/lesson_03/lesson_03_02.json";

import lesson_04_01 from "@/data/lesson_04/lesson_04_01.json";
import lesson_04_02 from "@/data/lesson_04/lesson_04_02.json";
import lesson_04_03 from "@/data/lesson_04/lesson_04_03.json";

const lessonDatas = {
  '1_1': lesson_01_01,
  '1_2': lesson_01_02,

  '2_1': lesson_02_01,
  '2_2': lesson_02_02,
  
  '3_1': lesson_03_01,
  '3_2': lesson_03_02,

  '4_1': lesson_04_01,
  '4_2': lesson_04_02,
  '4_3': lesson_04_03,
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
  2:[{
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
  ],
  4:[
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
  {
    id:3,
    value:'文章2',
    label:'文章2'
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
