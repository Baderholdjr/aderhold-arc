// GENERATED FILE: do not edit by hand.
// Source: instrument/items.yaml  ->  python -m arc build-collector
var ARC_INSTRUMENT = {
  "version": "1.0.0",
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
          "reverse": false
        },
        {
          "id": "A1.2",
          "text": "I understand how AI is meant to change my work over the next year.",
          "reverse": false
        },
        {
          "id": "A1.3",
          "text": "The message I hear about AI is about helping people do better work, not just cutting costs.",
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
          "reverse": false
        },
        {
          "id": "A2.2",
          "text": "I worry that AI will be used to replace my role.",
          "reverse": true
        },
        {
          "id": "A2.3",
          "text": "I can raise concerns about AI tools without it hurting how I'm seen.",
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
          "reverse": false
        },
        {
          "id": "A3.2",
          "text": "I have had to learn our AI tools mostly on my own time.",
          "reverse": true
        },
        {
          "id": "A3.3",
          "text": "I know where to go for help when I get stuck using an AI tool.",
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
          "reverse": false
        },
        {
          "id": "A4.2",
          "text": "I have seen concrete examples of colleagues getting good results with AI.",
          "reverse": false
        },
        {
          "id": "A4.3",
          "text": "The AI tools we have been given fit the work I actually do.",
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
          "reverse": false
        },
        {
          "id": "R1.2",
          "text": "When an AI tool gives an answer, I can usually tell how it got there.",
          "reverse": false
        },
        {
          "id": "R1.3",
          "text": "I am often expected to act on AI outputs I couldn't explain to someone else.",
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
          "reverse": false
        },
        {
          "id": "R2.2",
          "text": "I have been taught the common ways our AI tools make mistakes.",
          "reverse": false
        },
        {
          "id": "R2.3",
          "text": "I trust AI outputs about the right amount, neither too much nor too little.",
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
          "reverse": false
        },
        {
          "id": "R3.2",
          "text": "I often end up redoing AI work from scratch because I don't trust it.",
          "reverse": true
        },
        {
          "id": "R3.3",
          "text": "I sometimes accept AI outputs without checking because of time pressure.",
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
          "reverse": false
        },
        {
          "id": "R4.2",
          "text": "After AI errors, we learn what went wrong and what to watch for.",
          "reverse": false
        },
        {
          "id": "R4.3",
          "text": "One bad AI mistake has made me stop trusting a tool I used to rely on.",
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
          "reverse": false
        },
        {
          "id": "C1.2",
          "text": "My role and responsibilities have been updated to reflect how AI is used.",
          "reverse": false
        },
        {
          "id": "C1.3",
          "text": "Time saved by AI is redirected to higher-value work.",
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
          "reverse": false
        },
        {
          "id": "C2.2",
          "text": "The AI training I receive matches my experience level.",
          "reverse": false
        },
        {
          "id": "C2.3",
          "text": "Skill in working with AI is developed, recognized and rewarded here.",
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
          "reverse": false
        },
        {
          "id": "C3.2",
          "text": "People on my team can see AI differently (as a partner or as a tool) and still work well together.",
          "reverse": false
        },
        {
          "id": "C3.3",
          "text": "It is clear which parts of our work belong to people and which to AI.",
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
          "reverse": false
        },
        {
          "id": "C4.2",
          "text": "I worry that relying on AI is eroding important skills on my team.",
          "reverse": true
        },
        {
          "id": "C4.3",
          "text": "There is a plan for how people will build expertise as AI takes over routine tasks.",
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
          "reverse": false
        },
        {
          "id": "F1.2",
          "text": "If an AI-assisted decision goes wrong, I expect to take the blame alone.",
          "reverse": true
        },
        {
          "id": "F1.3",
          "text": "It is clear who is accountable for decisions made with AI.",
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
          "reverse": false
        },
        {
          "id": "F2.2",
          "text": "I have felt pressure to go along with an AI output I disagreed with.",
          "reverse": true
        },
        {
          "id": "F2.3",
          "text": "My manager supports me when I override an AI tool for good reason.",
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
          "reverse": false
        },
        {
          "id": "F3.2",
          "text": "Our performance measures reward the quality of human judgment, not just speed.",
          "reverse": false
        },
        {
          "id": "F3.3",
          "text": "Feedback from people using AI is used to improve the tools or how we use them.",
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
      ]
    }
  ],
  "openQuestion": "What one change would make AI most useful in your work?",
  "columns": [
    "response_id",
    "campaign",
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
    "open_text",
    "instrument_version"
  ]
};
