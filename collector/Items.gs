// GENERATED FILE: do not edit by hand.
// Source: instrument/items.yaml  ->  python -m arc build-collector
var ARC_INSTRUMENT = {
  "version": "1.1.0",
  "scale": [
    "Strongly disagree",
    "Disagree",
    "Neither agree nor disagree",
    "Agree",
    "Strongly agree"
  ],
  "pillars": [
    {
      "name": "Acceptance",
      "question": "Will people engage with AI, willingly?"
    },
    {
      "name": "Reliance",
      "question": "Do people trust AI the right amount?"
    },
    {
      "name": "Collaboration",
      "question": "Has the work been reorganized around human-AI teaming?"
    },
    {
      "name": "Foundation",
      "question": "Are the rules on blame, override and measurement fair and explicit?"
    }
  ],
  "dimensions": [
    {
      "code": "A1",
      "name": "Purpose & narrative clarity",
      "pillar": "Acceptance",
      "items": [
        {
          "id": "A1.1",
          "text": "Leadership has clearly explained why our organization is adopting AI.",
          "leaderText": "Our people would say leadership has clearly explained why we are adopting AI.",
          "reverse": false
        },
        {
          "id": "A1.2",
          "text": "I understand how AI is meant to change my work over the next year.",
          "leaderText": "Our people understand how AI is meant to change their work over the next year.",
          "reverse": false
        },
        {
          "id": "A1.3",
          "text": "The message I hear about AI is about helping people do better work, not just cutting costs.",
          "leaderText": "Our message about AI is about helping people do better work, not just cutting costs.",
          "reverse": false
        }
      ]
    },
    {
      "code": "A2",
      "name": "Role security & psychological safety",
      "pillar": "Acceptance",
      "items": [
        {
          "id": "A2.1",
          "text": "I feel safe admitting when I don't know how to use an AI tool.",
          "leaderText": "People here feel safe admitting when they don't know how to use an AI tool.",
          "reverse": false
        },
        {
          "id": "A2.2",
          "text": "I worry that AI will be used to replace my role.",
          "leaderText": "People here worry that AI will be used to replace their roles.",
          "reverse": true
        },
        {
          "id": "A2.3",
          "text": "I can raise concerns about AI tools without it hurting how I'm seen.",
          "leaderText": "People can raise concerns about AI tools without it hurting how they are seen.",
          "reverse": false
        }
      ]
    },
    {
      "code": "A3",
      "name": "Onboarding & enablement",
      "pillar": "Acceptance",
      "items": [
        {
          "id": "A3.1",
          "text": "I received training on our AI tools that was specific to my role.",
          "leaderText": "Our people have received AI training that is specific to their roles.",
          "reverse": false
        },
        {
          "id": "A3.2",
          "text": "I have had to learn our AI tools mostly on my own time.",
          "leaderText": "Our people have had to learn our AI tools mostly on their own time.",
          "reverse": true
        },
        {
          "id": "A3.3",
          "text": "I know where to go for help when I get stuck using an AI tool.",
          "leaderText": "Our people know where to go for help when they get stuck with an AI tool.",
          "reverse": false
        }
      ]
    },
    {
      "code": "A4",
      "name": "Demonstrated value",
      "pillar": "Acceptance",
      "items": [
        {
          "id": "A4.1",
          "text": "AI tools have made a real difference on at least one task I care about.",
          "leaderText": "AI tools have made a real difference on tasks our people care about.",
          "reverse": false
        },
        {
          "id": "A4.2",
          "text": "I have seen concrete examples of colleagues getting good results with AI.",
          "leaderText": "Our people have seen concrete examples of colleagues getting good results with AI.",
          "reverse": false
        },
        {
          "id": "A4.3",
          "text": "The AI tools we have been given fit the work I actually do.",
          "leaderText": "The AI tools we have provided fit the work our people actually do.",
          "reverse": false
        }
      ]
    },
    {
      "code": "R1",
      "name": "Explainability & transparency",
      "pillar": "Reliance",
      "items": [
        {
          "id": "R1.1",
          "text": "Our AI tools show enough reasoning or sources for me to judge their outputs.",
          "leaderText": "Our AI tools show enough reasoning or sources for people to judge their outputs.",
          "reverse": false
        },
        {
          "id": "R1.2",
          "text": "When an AI tool gives an answer, I can usually tell how it got there.",
          "leaderText": "When an AI tool gives an answer, our people can usually tell how it got there.",
          "reverse": false
        },
        {
          "id": "R1.3",
          "text": "I am often expected to act on AI outputs I couldn't explain to someone else.",
          "leaderText": "Our people are often expected to act on AI outputs they couldn't explain to someone else.",
          "reverse": true
        }
      ]
    },
    {
      "code": "R2",
      "name": "Trust calibration",
      "pillar": "Reliance",
      "items": [
        {
          "id": "R2.1",
          "text": "I know which tasks our AI tools are reliable for and which they are not.",
          "leaderText": "Our people know which tasks our AI tools are reliable for and which they are not.",
          "reverse": false
        },
        {
          "id": "R2.2",
          "text": "I have been taught the common ways our AI tools make mistakes.",
          "leaderText": "Our people have been taught the common ways our AI tools make mistakes.",
          "reverse": false
        },
        {
          "id": "R2.3",
          "text": "I trust AI outputs about the right amount, neither too much nor too little.",
          "leaderText": "Our people trust AI outputs about the right amount, neither too much nor too little.",
          "reverse": false
        }
      ]
    },
    {
      "code": "R3",
      "name": "Verification practice",
      "pillar": "Reliance",
      "items": [
        {
          "id": "R3.1",
          "text": "There are clear guidelines for how carefully to check AI outputs, based on the risk of the task.",
          "leaderText": "We have clear guidelines for how carefully to check AI outputs, based on the risk of the task.",
          "reverse": false
        },
        {
          "id": "R3.2",
          "text": "I often end up redoing AI work from scratch because I don't trust it.",
          "leaderText": "Our people often redo AI work from scratch because they don't trust it.",
          "reverse": true
        },
        {
          "id": "R3.3",
          "text": "I sometimes accept AI outputs without checking because of time pressure.",
          "leaderText": "Our people sometimes accept AI outputs without checking because of time pressure.",
          "reverse": true
        }
      ]
    },
    {
      "code": "R4",
      "name": "Failure response (\"flop protocol\")",
      "pillar": "Reliance",
      "items": [
        {
          "id": "R4.1",
          "text": "When an AI tool makes a significant mistake, there is a clear way to report it.",
          "leaderText": "When an AI tool makes a significant mistake, there is a clear way to report it.",
          "reverse": false
        },
        {
          "id": "R4.2",
          "text": "After AI errors, we learn what went wrong and what to watch for.",
          "leaderText": "After AI errors, we learn what went wrong and what to watch for.",
          "reverse": false
        },
        {
          "id": "R4.3",
          "text": "One bad AI mistake has made me stop trusting a tool I used to rely on.",
          "leaderText": "A single bad AI mistake has made people stop trusting a tool they used to rely on.",
          "reverse": true
        }
      ]
    },
    {
      "code": "C1",
      "name": "Workflow & role redesign",
      "pillar": "Collaboration",
      "items": [
        {
          "id": "C1.1",
          "text": "Our workflows have been redesigned to make use of AI, not just had AI added on top.",
          "leaderText": "Our workflows have been redesigned to make use of AI, not just had AI added on top.",
          "reverse": false
        },
        {
          "id": "C1.2",
          "text": "My role and responsibilities have been updated to reflect how AI is used.",
          "leaderText": "Roles and responsibilities have been updated to reflect how AI is used.",
          "reverse": false
        },
        {
          "id": "C1.3",
          "text": "Time saved by AI is redirected to higher-value work.",
          "leaderText": "Time saved by AI is redirected to higher-value work.",
          "reverse": false
        }
      ]
    },
    {
      "code": "C2",
      "name": "AI direction competency",
      "pillar": "Collaboration",
      "items": [
        {
          "id": "C2.1",
          "text": "I am confident giving AI tools clear instructions that get useful results.",
          "leaderText": "Our people are confident giving AI tools clear instructions that get useful results.",
          "reverse": false
        },
        {
          "id": "C2.2",
          "text": "The AI training I receive matches my experience level.",
          "leaderText": "The AI training we provide matches each person's experience level.",
          "reverse": false
        },
        {
          "id": "C2.3",
          "text": "Skill in working with AI is developed, recognized and rewarded here.",
          "leaderText": "Skill in working with AI is developed, recognized and rewarded here.",
          "reverse": false
        }
      ]
    },
    {
      "code": "C3",
      "name": "Teaming norms",
      "pillar": "Collaboration",
      "items": [
        {
          "id": "C3.1",
          "text": "My team has agreed norms for when and how we use AI.",
          "leaderText": "Our teams have agreed norms for when and how they use AI.",
          "reverse": false
        },
        {
          "id": "C3.2",
          "text": "People on my team can see AI differently (as a partner or as a tool) and still work well together.",
          "leaderText": "People who see AI differently (as a partner or as a tool) still work well together here.",
          "reverse": false
        },
        {
          "id": "C3.3",
          "text": "It is clear which parts of our work belong to people and which to AI.",
          "leaderText": "It is clear which parts of our work belong to people and which to AI.",
          "reverse": false
        }
      ]
    },
    {
      "code": "C4",
      "name": "Expertise pipeline",
      "pillar": "Collaboration",
      "items": [
        {
          "id": "C4.1",
          "text": "Newer staff still get the practice they need to build real expertise.",
          "leaderText": "Newer staff still get the practice they need to build real expertise.",
          "reverse": false
        },
        {
          "id": "C4.2",
          "text": "I worry that relying on AI is eroding important skills on my team.",
          "leaderText": "I worry that relying on AI is eroding important skills in our teams.",
          "reverse": true
        },
        {
          "id": "C4.3",
          "text": "There is a plan for how people will build expertise as AI takes over routine tasks.",
          "leaderText": "We have a plan for how people will build expertise as AI takes over routine tasks.",
          "reverse": false
        }
      ]
    },
    {
      "code": "F1",
      "name": "Accountability model",
      "pillar": "Foundation",
      "items": [
        {
          "id": "F1.1",
          "text": "I am judged on whether I used good judgment and checks, not on errors the AI makes on its own.",
          "leaderText": "We judge people on whether they used good judgment and checks, not on errors the AI makes on its own.",
          "reverse": false
        },
        {
          "id": "F1.2",
          "text": "If an AI-assisted decision goes wrong, I expect to take the blame alone.",
          "leaderText": "If an AI-assisted decision goes wrong, the employee involved would take the blame alone.",
          "reverse": true
        },
        {
          "id": "F1.3",
          "text": "It is clear who is accountable for decisions made with AI.",
          "leaderText": "It is clear who is accountable for decisions made with AI.",
          "reverse": false
        }
      ]
    },
    {
      "code": "F2",
      "name": "Right to override",
      "pillar": "Foundation",
      "items": [
        {
          "id": "F2.1",
          "text": "I have clear authority to overrule an AI recommendation.",
          "leaderText": "Our people have clear authority to overrule an AI recommendation.",
          "reverse": false
        },
        {
          "id": "F2.2",
          "text": "I have felt pressure to go along with an AI output I disagreed with.",
          "leaderText": "Our people feel pressure to go along with AI outputs they disagree with.",
          "reverse": true
        },
        {
          "id": "F2.3",
          "text": "My manager supports me when I override an AI tool for good reason.",
          "leaderText": "Managers here support people who override an AI tool for good reason.",
          "reverse": false
        }
      ]
    },
    {
      "code": "F3",
      "name": "Human-AI measurement",
      "pillar": "Foundation",
      "items": [
        {
          "id": "F3.1",
          "text": "We track whether AI tools are actually being used and actually helping.",
          "leaderText": "We track whether AI tools are actually being used and actually helping.",
          "reverse": false
        },
        {
          "id": "F3.2",
          "text": "Our performance measures reward the quality of human judgment, not just speed.",
          "leaderText": "Our performance measures reward the quality of human judgment, not just speed.",
          "reverse": false
        },
        {
          "id": "F3.3",
          "text": "Feedback from people using AI is used to improve the tools or how we use them.",
          "leaderText": "Feedback from people using AI is used to improve the tools or how we use them.",
          "reverse": false
        }
      ]
    }
  ],
  "behavioral": [
    {
      "id": "B1",
      "key": "use_freq",
      "text": "How often do you use the organization's AI tools for work?",
      "options": [
        {
          "label": "Never",
          "value": 1
        },
        {
          "label": "Monthly or less",
          "value": 2
        },
        {
          "label": "Weekly",
          "value": 3
        },
        {
          "label": "Several times a week",
          "value": 4
        },
        {
          "label": "Daily",
          "value": 5
        }
      ]
    },
    {
      "id": "B2",
      "key": "depth",
      "text": "For tasks AI could help with, roughly what share do you use it for?",
      "options": [
        {
          "label": "None",
          "value": 0
        },
        {
          "label": "About 25%",
          "value": 0.25
        },
        {
          "label": "About half",
          "value": 0.5
        },
        {
          "label": "About 75%",
          "value": 0.75
        },
        {
          "label": "All of them",
          "value": 1
        }
      ]
    },
    {
      "id": "B3",
      "key": "verify_share",
      "text": "Of the time AI saves you, how much goes to re-checking or redoing its work?",
      "options": [
        {
          "label": "None",
          "value": 0
        },
        {
          "label": "About 25%",
          "value": 0.25
        },
        {
          "label": "About half",
          "value": 0.5
        },
        {
          "label": "About 75%",
          "value": 0.75
        },
        {
          "label": "All of it",
          "value": 1
        }
      ]
    },
    {
      "id": "B4",
      "key": "error_seen",
      "text": "In the last 90 days, have you seen an AI error reach a customer, a decision or a final output?",
      "options": [
        {
          "label": "Yes",
          "value": 1
        },
        {
          "label": "No",
          "value": 0
        },
        {
          "label": "Not sure",
          "value": null
        }
      ]
    },
    {
      "id": "B5",
      "key": "train_hrs",
      "text": "Hours of AI training received in the last 12 months",
      "options": [
        {
          "label": "0",
          "value": 0
        },
        {
          "label": "1-2",
          "value": 1.5
        },
        {
          "label": "3-4",
          "value": 3.5
        },
        {
          "label": "5-9",
          "value": 7
        },
        {
          "label": "10+",
          "value": 12
        }
      ]
    },
    {
      "id": "B6",
      "key": "own_time_hrs",
      "text": "Hours spent learning AI tools on personal time in the last 3 months",
      "options": [
        {
          "label": "0",
          "value": 0
        },
        {
          "label": "1-5",
          "value": 3
        },
        {
          "label": "6-10",
          "value": 8
        },
        {
          "label": "11-20",
          "value": 15
        },
        {
          "label": "20+",
          "value": 25
        }
      ]
    },
    {
      "id": "B7",
      "key": "shadow_ai",
      "text": "In the last 30 days, have you used AI tools not approved by the organization?",
      "options": [
        {
          "label": "Yes",
          "value": 1
        },
        {
          "label": "No",
          "value": 0
        },
        {
          "label": "Prefer not to say",
          "value": null
        }
      ]
    },
    {
      "id": "B8",
      "key": "role",
      "text": "Your role",
      "options": [
        {
          "label": "Individual contributor",
          "value": "IC"
        },
        {
          "label": "People manager",
          "value": "MGR"
        },
        {
          "label": "Senior leader",
          "value": "SL"
        }
      ],
      "staff_only": true
    }
  ],
  "exposure": {
    "scale": [
      {
        "label": "Yes",
        "value": 1
      },
      {
        "label": "No",
        "value": 0
      },
      {
        "label": "Not sure",
        "value": null
      }
    ],
    "items": [
      {
        "id": "X.M1",
        "module": "M1",
        "targets": [
          "A1",
          "A2"
        ],
        "text": "Leadership has recently explained why we're using AI and what it means for our jobs.",
        "leader_text": "I have recently explained to my teams why we're using AI and what it means for their jobs."
      },
      {
        "id": "X.M2",
        "module": "M2",
        "targets": [
          "A2",
          "A3",
          "F2"
        ],
        "text": "My manager has coached me or my team on using AI tools.",
        "leader_text": "Managers in my area have been coaching their teams on using AI tools."
      },
      {
        "id": "X.M3",
        "module": "M3",
        "targets": [
          "A3",
          "A4"
        ],
        "text": "I received role-specific AI training during work time.",
        "leader_text": "My teams received role-specific AI training during work time."
      },
      {
        "id": "X.M4",
        "module": "M4",
        "targets": [
          "A4",
          "C1"
        ],
        "text": "My team took part in a session to find good uses for AI in our work.",
        "leader_text": "My teams took part in sessions to find good uses for AI in their work."
      },
      {
        "id": "X.M5",
        "module": "M5",
        "targets": [
          "R1",
          "R2"
        ],
        "text": "I've been shown where our AI tools are reliable and where they make mistakes.",
        "leader_text": "My teams have been shown where our AI tools are reliable and where they make mistakes."
      },
      {
        "id": "X.M6",
        "module": "M6",
        "targets": [
          "R3",
          "F2"
        ],
        "text": "I've been given clear rules on how carefully to check AI outputs for different kinds of tasks.",
        "leader_text": "My teams have clear rules on how carefully to check AI outputs for different kinds of tasks."
      },
      {
        "id": "X.M7",
        "module": "M7",
        "targets": [
          "R4",
          "F3"
        ],
        "text": "I know how to report an AI error, and I've seen errors followed up.",
        "leader_text": "We have a working process for reporting AI errors, and errors are followed up."
      },
      {
        "id": "X.M8",
        "module": "M8",
        "targets": [
          "C2"
        ],
        "text": "I've had training on giving AI instructions and checking its work, at my level.",
        "leader_text": "My teams have had leveled training on giving AI instructions and checking its work."
      },
      {
        "id": "X.M9",
        "module": "M9",
        "targets": [
          "C1",
          "C3"
        ],
        "text": "At least one of my team's workflows was redesigned around AI.",
        "leader_text": "At least one workflow in my area was redesigned around AI."
      },
      {
        "id": "X.M10",
        "module": "M10",
        "targets": [
          "C4"
        ],
        "text": "There's a structured way for newer staff to build expertise alongside AI.",
        "leader_text": "We have put a structured way in place for newer staff to build expertise alongside AI."
      },
      {
        "id": "X.M11",
        "module": "M11",
        "targets": [
          "F1",
          "F2",
          "F3"
        ],
        "text": "Leadership has changed policy on accountability for AI errors or the right to override AI.",
        "leader_text": "We have changed policy on accountability for AI errors or the right to override AI."
      },
      {
        "id": "X.M12",
        "module": "M12",
        "targets": [
          "R1"
        ],
        "text": "Our AI tools now show their reasoning or sources more clearly.",
        "leader_text": "Our AI tools now show their reasoning or sources more clearly."
      }
    ]
  },
  "change": {
    "prompt": "Compared with when this program started, how has each of these changed for you?",
    "leader_prompt": "Compared with when this program started, how has each of these changed in your organization?",
    "scale": [
      {
        "label": "Much worse",
        "value": -2
      },
      {
        "label": "Worse",
        "value": -1
      },
      {
        "label": "About the same",
        "value": 0
      },
      {
        "label": "Better",
        "value": 1
      },
      {
        "label": "Much better",
        "value": 2
      }
    ],
    "items": [
      {
        "id": "P1",
        "pillar": "Acceptance",
        "text": "How useful AI tools are in my work",
        "leader_text": "How useful AI tools are in our people's work"
      },
      {
        "id": "P2",
        "pillar": "Reliance",
        "text": "How well I can judge when to trust AI outputs",
        "leader_text": "How well our people judge when to trust AI outputs"
      },
      {
        "id": "P3",
        "pillar": "Collaboration",
        "text": "How well my team's work is organized around AI",
        "leader_text": "How well our teams' work is organized around AI"
      },
      {
        "id": "P4",
        "pillar": "Foundation",
        "text": "How safe I feel questioning or overriding AI",
        "leader_text": "How safe people feel questioning or overriding AI"
      },
      {
        "id": "P5",
        "pillar": "Overall",
        "text": "How manageable my AI-related workload and stress feel",
        "leader_text": "How manageable AI-related workload and stress feel for our people"
      }
    ]
  },
  "leadership": {
    "items": [
      {
        "id": "L1",
        "text": "Our organization has a written AI strategy with measurable goals.",
        "type": "likert"
      },
      {
        "id": "L2",
        "text": "I know what return we expect from our AI investments, and by when.",
        "type": "likert"
      },
      {
        "id": "L3",
        "text": "I am prepared to change policy so people are not blamed for errors the AI makes on its own.",
        "type": "likert"
      },
      {
        "id": "L4",
        "text": "I am prepared to formally protect employees' right to override AI.",
        "type": "likert"
      },
      {
        "id": "L5",
        "text": "We are funding AI training at the level the rollout needs.",
        "type": "likert"
      },
      {
        "id": "L6",
        "text": "Leaders here model good AI use themselves.",
        "type": "likert"
      },
      {
        "id": "L7",
        "text": "When do you expect our AI investment to pay for itself?",
        "type": "choice",
        "options": [
          {
            "label": "Under 6 months",
            "value": 1
          },
          {
            "label": "6-12 months",
            "value": 2
          },
          {
            "label": "1-2 years",
            "value": 3
          },
          {
            "label": "More than 2 years",
            "value": 4
          },
          {
            "label": "Don't know",
            "value": null
          }
        ]
      }
    ],
    "open_question": "What worries you most about AI in your organization?"
  },
  "openQuestion": "What one change would make AI most useful in your work?",
  "columns": [
    "response_id",
    "campaign",
    "engagement",
    "wave",
    "audience",
    "submitted_date",
    "consent_research",
    "role",
    "use_freq",
    "depth",
    "verify_share",
    "error_seen",
    "train_hrs",
    "own_time_hrs",
    "shadow_ai",
    "A1.1",
    "A1.2",
    "A1.3",
    "A2.1",
    "A2.2",
    "A2.3",
    "A3.1",
    "A3.2",
    "A3.3",
    "A4.1",
    "A4.2",
    "A4.3",
    "R1.1",
    "R1.2",
    "R1.3",
    "R2.1",
    "R2.2",
    "R2.3",
    "R3.1",
    "R3.2",
    "R3.3",
    "R4.1",
    "R4.2",
    "R4.3",
    "C1.1",
    "C1.2",
    "C1.3",
    "C2.1",
    "C2.2",
    "C2.3",
    "C3.1",
    "C3.2",
    "C3.3",
    "C4.1",
    "C4.2",
    "C4.3",
    "F1.1",
    "F1.2",
    "F1.3",
    "F2.1",
    "F2.2",
    "F2.3",
    "F3.1",
    "F3.2",
    "F3.3",
    "X.M1",
    "X.M2",
    "X.M3",
    "X.M4",
    "X.M5",
    "X.M6",
    "X.M7",
    "X.M8",
    "X.M9",
    "X.M10",
    "X.M11",
    "X.M12",
    "P1",
    "P2",
    "P3",
    "P4",
    "P5",
    "L1",
    "L2",
    "L3",
    "L4",
    "L5",
    "L6",
    "L7",
    "open_text",
    "instrument_version"
  ]
};
