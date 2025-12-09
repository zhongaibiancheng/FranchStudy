const lesson1Notes = {
  "source_title": "法语第一课 Notes 学习导航（A/B/C 分层 + 金句 + 训练模板）",
  "levels": {
    "A": [
      {
        "id": "pourcentage_pour_cent",
        "name_zh": "百分比表达",
        "name_fr": "le pourcentage / pour cent",
        "mini_rule": "法语里“百分之……”用“数字 + pour cent”。",
        "must_memorize": [
          { "fr": "un pour cent", "zh": "1%" },
          { "fr": "trois virgule deux pour cent", "zh": "3,2%" },
          { "fr": "dix pour cent", "zh": "10%" },
          { "fr": "cent pour cent", "zh": "100%" }
        ],
        "drills": [
          {
            "type": "substitution",
            "label_zh": "数字替换",
            "template_fr": "{N} pour cent",
            "hint_zh": "把 {N} 换成 1 / 10 / 50 / 100 / 250",
            "output_example": {
              "fr": "cinquante pour cent",
              "zh": "50%"
            }
          },
          {
            "type": "reading",
            "label_zh": "读法训练",
            "prompt_zh": "看到百分比，读出法语。",
            "items": [
              { "zh": "99,9%", "answer_fr": "quatre-vingt-dix-neuf virgule neuf pour cent" },
              { "zh": "3,2%", "answer_fr": "trois virgule deux pour cent" }
            ]
          },
          {
            "type": "mini_translation",
            "label_zh": "中译法（短句）",
            "items": [
              { "zh": "百分之十", "answer_fr": "dix pour cent" },
              { "zh": "百分之百", "answer_fr": "cent pour cent" }
            ]
          }
        ]
      },
      {
        "id": "dis_dites_call",
        "name_zh": "口语呼唤/强调：Dis / Dites",
        "name_fr": "Dis ! / Dites ! (impératif de dire)",
        "mini_rule": "dire 的命令式 dis/dites（donc）在口语中可用来呼唤对方或加强语气。",
        "must_memorize": [
          { "fr": "Dis !", "zh": "哎，喂！（用来叫人/引起注意）" },
          { "fr": "Dites !", "zh": "喂，您听我说！（更礼貌/对“您”）" }
        ],
        "drills": [
          {
            "type": "dialogue_fill",
            "label_zh": "对话开头填空",
            "prompt_zh": "用一句自然的口语呼唤开头。",
            "template_fr": "— {blank}, tu as une minute ?",
            "answer_fr": "Dis"
          },
          {
            "type": "role_switch",
            "label_zh": "tu / vous 切换",
            "prompt_zh": "把同一句话换成更礼貌的“您”。",
            "items": [
              {
                "from_fr": "Dis, vous avez du temps ?",
                "to_fr": "Dites, vous avez du temps ?",
                "zh_note": "对“您”用 dites 更自然。"
              }
            ]
          },
          {
            "type": "scenario",
            "label_zh": "情境反应",
            "prompt_zh": "你想叫住朋友/老师，用一句简短法语开场。",
            "answer_fr_options": ["Dis !", "Dites !"]
          }
        ]
      },
      {
        "id": "tu_elision_oral",
        "name_zh": "口语省音：tu + 元音/哑音 h",
        "name_fr": "élision de tu",
        "mini_rule": "口语中 tu 在元音或哑音 h 开头动词前常省音：tu as → t’as，tu es → t’es。",
        "must_memorize": [
          { "fr": "T’es contente cette fois-ci, Lina ?", "zh": "这回你高兴了吧，利娜？" },
          { "fr": "T’as du feu, Pascal ?", "zh": "你有火儿吗，帕斯卡尔？" },
          { "fr": "T’es venue hier, Julie ?", "zh": "朱莉，你昨天来过吧？" },
          { "fr": "Où est-ce que t’habites ?", "zh": "你住哪儿呀？" }
        ],
        "drills": [
          {
            "type": "pair_transform",
            "label_zh": "完整形式 ↔ 口语省音",
            "prompt_zh": "把句子改成更口语的形式。",
            "items": [
              {
                "from_fr": "Tu es contente cette fois-ci ?",
                "to_fr": "T’es contente cette fois-ci ?",
                "zh_note": "tu es → t’es"
              },
              {
                "from_fr": "Tu as du temps ce soir ?",
                "to_fr": "T’as du temps ce soir ?",
                "zh_note": "tu as → t’as"
              }
            ]
          },
          {
            "type": "expand",
            "label_zh": "口语还原",
            "prompt_zh": "把省音句还原成标准书面形式。",
            "items": [
              { "fr": "T’es venue hier ?", "answer_fr": "Tu es venue hier ?" },
              { "fr": "T’habites où ?", "answer_fr": "Tu habites où ?" }
            ]
          },
          {
            "type": "choice",
            "label_zh": "选择正确口语形式",
            "prompt_zh": "下面哪一个更像自然口语？",
            "items": [
              {
                "options_fr": ["Tu es intéressée ?", "T’es intéressée ?"],
                "answer_index": 2,
                "zh_note": "口语更常用省音。"
              }
            ]
          }
        ]
      },
      {
        "id": "il_y_a_ellipsis_oral",
        "name_zh": "口语省略：il y a → y a",
        "name_fr": "ellipse de il y a",
        "mini_rule": "口语中无人称句 il y a 的 il 可省略：il y a → y a。",
        "must_memorize": [
          { "fr": "Mais papa, y a encore moi !", "zh": "可是，爸爸，还有我呢！" },
          { "fr": "Y a quelqu’un (à la maison) ?", "zh": "（家里）有人吗？" },
          { "fr": "Michel, y a un problème que je comprends pas.", "zh": "米歇尔，有个问题我不懂。" }
        ],
        "drills": [
          {
            "type": "pair_transform",
            "label_zh": "标准 ↔ 口语",
            "prompt_zh": "把句子改成口语省略形式。",
            "items": [
              {
                "from_fr": "Il y a un problème.",
                "to_fr": "Y a un problème.",
                "zh_note": "省略 il"
              }
            ]
          },
          {
            "type": "dialogue_fill",
            "label_zh": "对话填空",
            "prompt_zh": "完成一句自然的口语问句。",
            "template_fr": "— {blank} quelqu’un ?",
            "answer_fr": "Y a"
          },
          {
            "type": "notice",
            "label_zh": "使用提醒",
            "prompt_zh": "这类省略更偏口语，写作时要谨慎。",
            "checklist_zh": ["口语/对话可用", "正式写作尽量用 il y a"]
          }
        ]
      },
      {
        "id": "theme_vacances_basic",
        "name_zh": "度假主题基础词组",
        "name_fr": "vocabulaire des vacances (base)",
        "mini_rule": "第一课围绕“假期/外出/旅行”，先把高频名词与固定搭配整体记。",
        "must_memorize": [
          { "fr": "prendre des vacances", "zh": "度假" },
          { "fr": "partir en vacances", "zh": "外出度假" },
          { "fr": "jour de repos", "zh": "休息日" },
          { "fr": "congé de maladie", "zh": "病假" }
        ],
        "drills": [
          {
            "type": "substitution",
            "label_zh": "名词替换",
            "template_fr": "Je prends {N}.",
            "hint_zh": "{N} 可替换：des vacances / un congé / un jour de repos",
            "output_example": {
              "fr": "Je prends des vacances.",
              "zh": "我要去度假/我休假。"
            }
          },
          {
            "type": "choice",
            "label_zh": "搭配选择",
            "prompt_zh": "选择更自然的搭配。",
            "items": [
              {
                "options_fr": ["partir en vacances", "partir de vacances"],
                "answer_index": 1,
                "zh_note": "固定搭配是 partir en vacances。"
              }
            ]
          },
          {
            "type": "mini_translation",
            "label_zh": "中译法",
            "items": [
              { "zh": "我想去度假。", "answer_fr": "Je veux prendre des vacances." },
              { "zh": "我们要外出度假。", "answer_fr": "Nous allons partir en vacances." }
            ]
          }
        ]
      }
    ],
    "B": [
      {
        "id": "que_complement_clause",
        "name_zh": "que 引导的宾语从句",
        "name_fr": "proposition complétive avec que",
        "mini_rule": "dire / penser / comprendre / espérer / savoir / croire 等后可接 que 从句作宾语。",
        "must_memorize": [
          { "fr": "J’espère qu’on ne restera plus chez nous.", "zh": "我希望咱们别再老呆在家里了。" },
          { "fr": "Il dit qu’il partira demain.", "zh": "他说他明天走。" },
          { "fr": "Je sais qu’on pourra le faire.", "zh": "我知道他们能把这件事情做好。" },
          { "fr": "Pensez-vous qu’elle viendra ?", "zh": "您想她会来吗？" }
        ],
        "drills": [
          {
            "type": "substitution",
            "label_zh": "主句动词替换",
            "template_fr": "Je {V} que {S} {V2}.",
            "hint_zh": "{V} 可替换：pense / comprends / sais / crois / espère",
            "output_example": {
              "fr": "Je crois qu’il viendra.",
              "zh": "我相信他会来。"
            }
          },
          {
            "type": "combine",
            "label_zh": "合句",
            "prompt_zh": "把两句话合成一句 que 从句。",
            "items": [
              {
                "zh": "我希望。我们不再老待在家里。",
                "answer_fr": "J’espère qu’on ne restera plus chez nous."
              }
            ]
          },
          {
            "type": "choice",
            "label_zh": "是否需要 que？",
            "prompt_zh": "判断此处是否应该用 que 引导从句。",
            "items": [
              {
                "zh": "我知道他们能做到。",
                "answer_fr": "Je sais qu’on pourra le faire."
              }
            ]
          }
        ]
      },
      {
        "id": "avoir_du_temps_vs_avoir_le_temps_de",
        "name_zh": "两种“有时间/有空”表达",
        "name_fr": "avoir du temps / avoir le temps de",
        "mini_rule": "avoir du temps 表“有空”；avoir le temps de + 动词原形 表“有时间做某事”。",
        "must_memorize": [
          { "fr": "Nous aurons le temps de faire une petite promenade à pied.", "zh": "咱们还会有时间去散散步。" },
          { "fr": "Tu as du temps ce soir ?", "zh": "你今晚有空儿吗？" },
          { "fr": "Vous avez le temps de m’accompagner à la gare ?", "zh": "您有时间送我去火车站吗？" }
        ],
        "drills": [
          {
            "type": "qa",
            "label_zh": "问答模板",
            "template_fr": "— Tu as du temps ce soir ? — Oui, j’en ai. / Non, je n’en ai pas.",
            "hint_zh": "把 ce soir 换成 demain / ce week-end"
          },
          {
            "type": "substitution",
            "label_zh": "动作替换",
            "template_fr": "J’ai le temps de {Vinf}.",
            "hint_zh": "{Vinf} 可替换：faire une promenade / travailler / réviser",
            "output_example": {
              "fr": "J’ai le temps de réviser.",
              "zh": "我有时间复习。"
            }
          },
          {
            "type": "mini_translation",
            "label_zh": "中译法",
            "items": [
              { "zh": "我今晚有空。", "answer_fr": "J’ai du temps ce soir." },
              { "zh": "我有时间散步。", "answer_fr": "J’ai le temps de faire une promenade." }
            ]
          }
        ]
      },
      {
        "id": "si_present_futur_l1",
        "name_zh": "si 引导的现实条件句（本课出现）",
        "name_fr": "Si + présent, futur",
        "mini_rule": "现实可能发生的条件：Si + 现在时，主句常用将来时。",
        "must_memorize": [
          {
            "fr": "Si vous êtes sportif et bien entraîné, vous descendrez les torrents en canoë-kayak.",
            "zh": "如果您是运动型的人并且训练有素，您就会乘皮划艇顺流而下。"
          }
        ],
        "drills": [
          {
            "type": "substitution",
            "label_zh": "条件替换",
            "template_fr": "Si tu es {Adj}, tu {Vfutur}.",
            "hint_zh": "{Adj} 可替换：sportif / prudent / prêt；{Vfutur} 可替换：réussiras / iras / feras",
            "output_example": {
              "fr": "Si tu es prêt, tu partiras.",
              "zh": "如果你准备好了，你就会出发。"
            }
          },
          {
            "type": "reorder",
            "label_zh": "顺序互换",
            "prompt_zh": "把 si 从句放到句末或句首。",
            "items": [
              {
                "from_fr": "Vous descendrez les torrents en canoë-kayak si vous êtes sportif et bien entraîné.",
                "to_fr": "Si vous êtes sportif et bien entraîné, vous descendrez les torrents en canoë-kayak."
              }
            ]
          },
          {
            "type": "choice",
            "label_zh": "时态选择",
            "prompt_zh": "判断主句更自然用哪种时态。",
            "items": [
              {
                "fr": "Si tu es libre demain, nous _____ (aller) au cinéma.",
                "answer_fr": "irons",
                "zh_note": "现实条件句常用 futur。"
              }
            ]
          }
        ]
      },
      {
        "id": "au_dela_de_par_endroits",
        "name_zh": "两组高频短语：au-delà de / par endroits",
        "name_fr": "au-delà de / par endroits",
        "mini_rule": "au-delà de 表“在……那边/超越/超过”；par endroits 表“这儿那儿/某些地方”。",
        "must_memorize": [
          { "fr": "C’est au-delà de mes capacités.", "zh": "这已超出我的能力范围。" },
          { "fr": "Nos champs se trouvent au-delà de la rivière.", "zh": "我们的地在河对岸。" },
          { "fr": "Au-delà de 500 kilos, la voiture tombera en panne.", "zh": "汽车负载超过500公斤就会抛锚。" },
          { "fr": "Il y a des fautes d’orthographe par endroits.", "zh": "好几个地方有拼写错误。" },
          { "fr": "La nappe est tachée par endroits.", "zh": "桌布上多处染了污渍。" }
        ],
        "drills": [
          {
            "type": "choice",
            "label_zh": "选短语",
            "prompt_zh": "根据中文意思选择 au-delà de 或 par endroits。",
            "items": [
              {
                "zh": "这超出我的能力。",
                "answer_fr": "C’est au-delà de mes capacités."
              },
              {
                "zh": "这篇文章某些地方有错误。",
                "answer_fr": "Il y a des erreurs par endroits."
              }
            ]
          },
          {
            "type": "substitution",
            "label_zh": "名词替换（au-delà de）",
            "template_fr": "Au-delà de {N}, {S} {V}.",
            "hint_zh": "{N} 可替换：500 kilos / 3 heures / 10 minutes",
            "output_example": {
              "fr": "Au-delà de trois heures, je suis fatigué(e).",
              "zh": "超过三小时我就累了。"
            }
          },
          {
            "type": "rewrite",
            "label_zh": "par endroits 造句",
            "template_fr": "{Objet} est {Adj} par endroits.",
            "hint_zh": "{Objet} 可替换：le texte / la table / la route；{Adj} 可替换：sale / abîmé",
            "output_example": {
              "fr": "La route est abîmée par endroits.",
              "zh": "这条路有些地方破损。"
            }
          }
        ]
      }
    ],
    "C": [
      {
        "id": "sportif_en_chambre_quoi_idiom",
        "name_zh": "讽刺性表达：只说不练 + 口语 quoi",
        "name_fr": "sportif en chambre / quoi",
        "mini_rule": "en chambre 可表示“在家/室内”，也可讽刺“纸上谈兵/空谈”；quoi 常用于口语中结束解释或列举。",
        "must_memorize": [
          { "fr": "Sportif en chambre, quoi !", "zh": "说来说去也就是个只说不练的运动员！" },
          { "fr": "C’est un capitaine, un militaire quoi !", "zh": "他是个上尉，就是个当兵的！" },
          { "fr": "Il arrive dans 48 heures, après-demain quoi !", "zh": "他48小时后到，也就是后天！" },
          { "fr": "Elle a fait le ménage, la lessive, les courses, la cuisine, tout quoi.", "zh": "她收拾了房间、洗了衣服、买了东西、做了饭，总而言之，什么都干了。" }
        ],
        "drills": [
          {
            "type": "recognition",
            "label_zh": "阅读识别",
            "prompt_zh": "看到句末 quoi，理解为“总之/就是这样”，不必硬翻成疑问词。",
            "checklist_zh": [
              "多见口语",
              "用于结束解释/列举",
              "考试以理解为主"
            ]
          },
          {
            "type": "rewrite",
            "label_zh": "去掉 quoi 仍保持句意",
            "prompt_zh": "把句子改成更中性表达。",
            "items": [
              {
                "from_fr": "C’est un capitaine, un militaire quoi !",
                "to_fr": "C’est un capitaine, un militaire.",
                "zh_note": "去掉 quoi 语气变中性。"
              }
            ]
          },
          {
            "type": "scenario",
            "label_zh": "情境造句（理解应用）",
            "prompt_zh": "用“…, quoi !”补一句口语总结。",
            "template_fr": "Il parle beaucoup mais il ne fait rien, un {N} en chambre, quoi !",
            "hint_zh": "{N} 可替换：sportif / général / politicien",
            "output_example": {
              "fr": "Il parle beaucoup mais il ne fait rien, un politicien en chambre, quoi !",
              "zh": "他光说不练，简直是个空头政治家！"
            }
          }
        ]
      },
      {
        "id": "descendre_transitif_note",
        "name_zh": "descendre 及物用法提示（识别）",
        "name_fr": "descendre (verbe transitif) + avoir",
        "mini_rule": "descendre 作直接及物动词时（有直接宾语），复合过去时用 avoir。",
        "must_memorize": [
          { "fr": "Peux-tu me descendre ce tableau, s’il te plaît ?", "zh": "你能帮我把这幅画摘下来吗？" },
          { "fr": "On a descendu cet avion.", "zh": "有人击落了这架飞机。" },
          { "fr": "Elle a descendu l’escalier quatre à quatre.", "zh": "她三步并作两步地匆匆下了楼。" }
        ],
        "drills": [
          {
            "type": "aux_choice",
            "label_zh": "助动词判断（阅读型）",
            "prompt_zh": "判断复合过去时该用 avoir 还是 être。",
            "items": [
              {
                "fr": "Elle _____ descendu l’escalier quatre à quatre.",
                "answer_fr": "a",
                "zh_note": "此处表示“（快速）走下楼梯”的动作描述，教材注释强调及物意义时用 avoir。"
              }
            ]
          },
          {
            "type": "object_hint",
            "label_zh": "看宾语做判断",
            "prompt_zh": "看到 descendre + 直接宾语（tableau/avion 等），优先想到 avoir。",
            "checklist_zh": [
              "先找有没有直接宾语",
              "有宾语 → 倾向 avoir",
              "考试优先按课本规则"
            ]
          },
          {
            "type": "mini_translation",
            "label_zh": "中译法（识别应用）",
            "items": [
              { "zh": "你能帮我把那幅画拿下来吗？", "answer_fr": "Peux-tu me descendre ce tableau ?" }
            ]
          }
        ]
      },
      {
        "id": "cultural_loire_chateaux_l1",
        "name_zh": "卢瓦尔河古堡群（文化背景）",
        "name_fr": "les châteaux de la Loire",
        "mini_rule": "地理文化注释帮助理解场景与旅行话题，初中阶段知道“这是法国著名古堡群”即可。",
        "must_memorize": [
          { "fr": "les châteaux de la Loire", "zh": "卢瓦尔河古堡群。" }
        ],
        "drills": [
          {
            "type": "reading_note",
            "label_zh": "阅读提示",
            "prompt_zh": "看到文化注释时，你的目标不是背细节数据，而是理解文本语境。",
            "checklist_zh": [
              "知道这是法国著名旅游文化地标",
              "理解对话/课文为什么提到它",
              "可作为写作素材加分"
            ]
          }
        ]
      }
    ]
  }
}

export default lesson1Notes;