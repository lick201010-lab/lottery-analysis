// English SEO content for key topic pages (manually translated).
// Only topics present here get an /en/ route + EN switcher option.
export const seoTopicsEn = {
  "marksix-results": {
    path: "/marksix/results",
    game: "Mark Six",
    eyebrow: "MARKSIX RESULTS",
    title: "Hong Kong Mark Six Results & Draw History",
    description:
      "Check recent Hong Kong Mark Six winning numbers, the 6 main numbers and the extra number, draw dates and data sources. For data reference and entertainment only.",
    summary:
      "This page explains how to read Mark Six results — the 6 drawn numbers plus 1 extra number — along with draw dates and where the data comes from.",
    keyPoints: ["6 main numbers + 1 extra number (1-49)", "Draw dates and numbers per official announcement", "History is for review, not prediction"],
    sections: [
      {
        heading: "What a Mark Six result contains",
        body:
          "Each Mark Six draw shows a draw number, draw date, 6 main numbers and 1 extra number (all from 1 to 49). The 6 main numbers decide the top prize; the extra number only affects certain lower prize tiers.",
      },
      {
        heading: "How to read past results",
        body:
          "When reviewing history, confirm the draw number and date first, then look at colour, high/low and odd/even distribution. Past results only describe what happened — they cannot tell you the next draw.",
      },
      {
        heading: "Data source and updates",
        body:
          "We compile data from publicly available Hong Kong draw results. If a page differs from the official announcement, the official announcement prevails.",
      },
    ],
    faq: [
      { q: "When are Mark Six results updated?", a: "Usually right after each draw. Mark Six is normally drawn on Tuesday, Thursday and Saturday; exact timing follows the official announcement." },
      { q: "Does the extra number decide the jackpot?", a: "No. The Mark Six jackpot is decided by the 6 main numbers; the extra number only affects certain secondary prize tiers." },
    ],
    related: [
      { label: "Browse draw history", path: "/data" },
      { label: "Number frequency", path: "/marksix/frequency" },
      { label: "Game rules", path: "/marksix/rules" },
    ],
    dataset: {
      name: "Hong Kong Mark Six historical results",
      description: "Historical Hong Kong Mark Six draw records: draw number, draw date, 6 main numbers and 1 extra number.",
      variableMeasured: ["Draw number", "Draw date", "Main numbers", "Extra number"],
    },
  },
  "marksix-rules": {
    path: "/marksix/rules",
    game: "Mark Six",
    eyebrow: "MARKSIX RULES",
    title: "Mark Six Rules: Main Numbers & Extra Number Explained",
    description:
      "Understand Mark Six rules — the 6 main numbers, the extra number, draw numbers and prize conditions. For rule reference and entertainment only.",
    summary:
      "A clear explanation of Mark Six: 6 main numbers, 1 extra number, the draw schedule and how prize tiers are structured.",
    keyPoints: ["Main numbers are the core result", "Extra number affects some prize tiers", "Prize rules per official announcement"],
    sections: [
      {
        heading: "Main numbers and the extra number",
        body:
          "Each draw produces 6 main numbers and 1 extra number, all from 1 to 49. The main numbers are the core; the extra number serves as a supplementary condition for certain prizes. They should be displayed separately, not with equal weight.",
      },
      {
        heading: "Draw number and timing",
        body:
          "A draw number identifies a specific draw and the date confirms when it happened. Draw numbers restart each year, so always check year, draw number and date together when reading history.",
      },
      {
        heading: "Understanding prizes",
        body:
          "Prize tiers depend on how many main numbers match and whether the extra number is involved. Actual prize names, winning counts and amounts follow the official announcement.",
      },
    ],
    faq: [
      { q: "How many numbers are drawn in Mark Six?", a: "Usually 6 main numbers plus 1 extra number — 7 in total." },
      { q: "Should the main and extra numbers be read separately?", a: "Yes. They play different roles in the prize conditions, so analysis pages should also show them separately." },
    ],
    related: [
      { label: "Rules overview", path: "/guide" },
      { label: "Winning odds", path: "/marksix/odds" },
      { label: "Prize calculator", path: "/jackpot" },
    ],
  },
  "marksix-history": {
    path: "/marksix/history",
    game: "Mark Six",
    eyebrow: "MARKSIX HISTORY",
    title: "Mark Six Historical Results & Yearly Archive",
    description:
      "Look up Hong Kong Mark Six historical results by year and draw number, with main and extra numbers and draw dates. For data reference and entertainment only.",
    summary:
      "This page helps users searching for Mark Six draw history read records by year, draw number and number fields, and treat history as a sample for review only.",
    keyPoints: ["Archived by year", "6 main numbers + 1 extra number", "History is for lookup and review only"],
    sections: [
      {
        heading: "How to look up Mark Six history",
        body:
          "Enter the archive by year, then open a draw number to see its date, 6 main numbers and 1 extra number. We organise history into a single consistent view to reduce jumping between pages.",
      },
      {
        heading: "Why check year and draw number together",
        body:
          "The draw number marks the order within a year and the date confirms the actual draw time. Across years, draw numbers alone can be confusing, so check year, number and date together.",
      },
      {
        heading: "The limits of historical data",
        body:
          "History helps you review number distribution, colour structure and ranges, but it cannot judge the next draw. We only provide data organisation and display, not any participation advice.",
      },
    ],
    faq: [
      { q: "How far back does Mark Six history go?", a: "We organise results across many years; exact coverage depends on available public data." },
      { q: "Can history predict future numbers?", a: "No. Draws are random; historical data cannot guarantee or predict future results." },
    ],
    related: [
      { label: "Browse draw history", path: "/data" },
      { label: "Latest results", path: "/marksix/results" },
      { label: "Number frequency", path: "/marksix/frequency" },
    ],
    dataset: {
      name: "Hong Kong Mark Six historical results",
      description: "Yearly archive of Hong Kong Mark Six draws: draw number, date, 6 main numbers and 1 extra number.",
      variableMeasured: ["Draw number", "Draw date", "Main numbers", "Extra number"],
    },
  },
  "marksix-odds": {
    path: "/marksix/odds",
    game: "Mark Six",
    eyebrow: "MARKSIX ODDS",
    title: "Mark Six Winning Odds & Prize Conditions Explained",
    description:
      "Understand Mark Six prize conditions, combination counts and probability as a maths concept. Draws are random; for data reference and entertainment only.",
    summary:
      "This page frames Mark Six odds as a combinatorics problem, helping you understand prize difficulty rather than predict outcomes.",
    keyPoints: ["Odds come from combination counts", "Each draw is a random event", "History cannot change single-draw odds"],
    sections: [
      {
        heading: "Where the odds come from",
        body:
          "Odds can be derived from the pool of available numbers and how many you need to match. Understanding what probability means matters more than memorising the exact figures.",
      },
      {
        heading: "Differences between prize tiers",
        body:
          "Different tiers correspond to different conditions — how many main numbers match and whether the extra number is involved. Stricter conditions generally mean lower theoretical odds.",
      },
      {
        heading: "Why odds are not a prediction",
        body:
          "Probability describes the mathematical nature of long-run random events, not a specific draw. Any single draw can differ from the historical distribution.",
      },
    ],
    faq: [
      { q: "Can this page predict the next draw?", a: "No. It only explains rules and combination counts; it cannot judge a specific result." },
      { q: "Does past frequency change the next draw's odds?", a: "No. Past frequency is a sample and cannot change a random draw." },
    ],
    related: [
      { label: "Odds overview", path: "/odds" },
      { label: "Number frequency", path: "/marksix/frequency" },
      { label: "Responsible play", path: "/responsible" },
    ],
  },
  "marksix-frequency": {
    path: "/marksix/frequency",
    game: "Mark Six",
    eyebrow: "MARKSIX FREQUENCY",
    title: "Mark Six Number Frequency, Hot & Cold Stats",
    description:
      "Mark Six number appearance counts, hot/cold numbers, missing streaks and range distribution from historical draws. Draws are random; for reference only.",
    summary:
      "This page explains what frequency, hot/cold and missing statistics mean for Mark Six, treating history as a distribution sample.",
    keyPoints: ["Frequency = past appearance count", "Hot/cold reflects past samples only", "Missing streaks do not imply a 'due' number"],
    sections: [
      {
        heading: "How to read number frequency",
        body:
          "Frequency counts how often a number has appeared historically. It helps you understand sample distribution but cannot prove a number is more likely next time.",
      },
      {
        heading: "Using hot and cold numbers correctly",
        body:
          "Hot numbers appear more often recently or overall; cold numbers appear less. They suit review, not result judgement.",
      },
      {
        heading: "The boundary of missing stats",
        body:
          "A missing streak shows how many draws since a number last appeared. A longer streak only means a longer past gap — it does not mean the next draw will fill it.",
      },
    ],
    faq: [
      { q: "Can hot/cold numbers be used to judge results?", a: "No. They are historical indicators only; draws are random." },
      { q: "Why does a number's frequency change?", a: "Every draw updates the sample, so counts, missing streaks and hot/cold rankings shift accordingly." },
    ],
    related: [
      { label: "Open frequency analysis", path: "/frequency" },
      { label: "Latest results", path: "/marksix/results" },
      { label: "Game rules", path: "/marksix/rules" },
    ],
  },
  "ssq-results": {
    path: "/ssq/results",
    game: "Shuangseqiu (SSQ)",
    eyebrow: "SSQ RESULTS",
    title: "Shuangseqiu (Double-Color Ball) Results & History",
    description:
      "Check recent Shuangseqiu (SSQ) winning numbers — 6 red balls and 1 blue ball — draw dates and history. For data reference and entertainment only.",
    summary:
      "This page organises SSQ results, focusing on the difference between the 6 red balls and the 1 blue ball.",
    keyPoints: ["6 red balls (01-33) + 1 blue ball (01-16)", "The blue ball is part of the jackpot condition", "Results per official announcement"],
    sections: [
      {
        heading: "What an SSQ result contains",
        body:
          "Each SSQ draw shows a draw number, date, 6 red balls (01-33) and 1 blue ball (01-16). The blue ball is not a decorative extra — it is part of the top-prize condition.",
      },
      {
        heading: "Why the blue ball is shown separately",
        body:
          "Unlike Mark Six's extra number, the SSQ blue ball is essential to the jackpot. Display and analysis should keep red and blue balls in separate zones.",
      },
      {
        heading: "Using historical results",
        body:
          "History suits lookup, review and distribution stats. Draws are random; historical data cannot guarantee future results.",
      },
    ],
    faq: [
      { q: "Is the SSQ blue ball required for the jackpot?", a: "Yes. The SSQ top prize generally requires all 6 red balls and the 1 blue ball to match." },
      { q: "Where can I view SSQ history?", a: "On our history page, or via the SSQ topic pages organised by data dimension." },
    ],
    related: [
      { label: "Browse draw history", path: "/data" },
      { label: "SSQ frequency", path: "/ssq/frequency" },
      { label: "SSQ rules", path: "/ssq/rules" },
    ],
    dataset: {
      name: "Shuangseqiu (SSQ) historical results",
      description: "Historical Shuangseqiu draw records: draw number, date, 6 red balls and 1 blue ball.",
      variableMeasured: ["Draw number", "Draw date", "Red balls", "Blue ball"],
    },
  },
  "ssq-rules": {
    path: "/ssq/rules",
    game: "Shuangseqiu (SSQ)",
    eyebrow: "SSQ RULES",
    title: "Shuangseqiu Rules: Red & Blue Balls Explained",
    description:
      "Understand Shuangseqiu (SSQ) rules — 6 red + 1 blue, prize conditions and common terms. For rule reference and entertainment only.",
    summary:
      "A clear explanation of SSQ red and blue balls and why the blue ball is essential to the jackpot.",
    keyPoints: ["Red balls from 01-33", "Blue ball from 01-16", "The jackpot includes the blue ball"],
    sections: [
      {
        heading: "The 6-red + 1-blue structure",
        body:
          "Each SSQ ticket has 6 red balls and 1 blue ball with different ranges. Display and analysis should clearly separate the two zones.",
      },
      {
        heading: "The blue ball's role in prizes",
        body:
          "The blue ball is very important to SSQ prizes, especially the jackpot — it should never be treated as optional.",
      },
      {
        heading: "Review with draw data",
        body:
          "When reviewing SSQ data, combine draw number, date, red balls, blue ball, sum, odd/even and ranges. All review is for understanding historical data only.",
      },
    ],
    faq: [
      { q: "How many numbers are on one SSQ ticket?", a: "Usually 6 red balls and 1 blue ball." },
      { q: "Is the SSQ blue ball the same as the Mark Six extra number?", a: "No. The SSQ blue ball is part of the jackpot condition; the Mark Six extra number is only a supplementary condition for certain prizes." },
    ],
    related: [
      { label: "Rules overview", path: "/guide" },
      { label: "SSQ odds", path: "/ssq/odds" },
      { label: "Responsible play", path: "/responsible" },
    ],
  },
  "ssq-frequency": {
    path: "/ssq/frequency",
    game: "Shuangseqiu (SSQ)",
    eyebrow: "SSQ FREQUENCY",
    title: "SSQ Number Frequency: Red & Blue Ball Stats",
    description:
      "Shuangseqiu red and blue ball appearance counts, hot/cold and missing streaks from history. Draws are random; for data reference only.",
    summary:
      "This page explains SSQ red and blue ball frequency, hot/cold and missing stats as a way to read history as a sample.",
    keyPoints: ["Count red and blue balls separately", "Blue ball range is 01-16", "Hot/cold and missing do not imply future results"],
    sections: [
      {
        heading: "Red ball frequency",
        body:
          "Red ball frequency counts how often each of 01-33 has appeared. It reflects sample differences but does not represent the next result.",
      },
      {
        heading: "Blue ball frequency",
        body:
          "The blue ball has a smaller range and should be counted on its own. It affects prize conditions and is also worth observing for appearance and missing streaks.",
      },
      {
        heading: "Hot/cold and missing",
        body:
          "Hot/cold and missing streaks are historical indicators, suitable for review and never to be read as participation advice.",
      },
    ],
    faq: [
      { q: "Can red and blue balls be counted together?", a: "Not recommended. They have different ranges and prize roles and should be counted separately." },
      { q: "Is a long-missing blue ball more likely next draw?", a: "No. A missing streak only describes a past gap, not the future draw." },
    ],
    related: [
      { label: "Open frequency analysis", path: "/frequency" },
      { label: "SSQ results", path: "/ssq/results" },
      { label: "SSQ odds", path: "/ssq/odds" },
    ],
  },
  "qxc-results": {
    path: "/qxc/results",
    game: "Qixingcai (QXC)",
    eyebrow: "QXC RESULTS",
    title: "Qixingcai (Seven-Star Lottery) Results",
    description:
      "Check recent China Sports Lottery Qixingcai (QXC) numbers — 6 front digits and 1 back digit — draw dates and source. For data reference only.",
    summary:
      "This page organises QXC results and its number structure: 6 front-zone digits (0-9) plus 1 back-zone digit (0-14).",
    keyPoints: ["6 front digits, each 0-9", "1 back digit, range 0-14", "Draw dates per official announcement"],
    sections: [
      {
        heading: "What a Qixingcai result contains",
        body:
          "Each QXC draw shows a draw number, date, 6 front-zone digits (each 0-9) and 1 back-zone digit (0-14). The front zone is positional; the back zone is a single independent digit.",
      },
      {
        heading: "How to read past results",
        body:
          "Confirm the draw number and date first, then look at each front-zone digit and the back-zone digit. History describes the past, not the next draw.",
      },
      {
        heading: "Data source and updates",
        body:
          "We compile from publicly available China Sports Lottery announcements. If a page differs from the official announcement, the official announcement prevails.",
      },
    ],
    faq: [
      { q: "When is Qixingcai drawn?", a: "Usually Tuesday, Friday and Sunday; exact timing per the official announcement." },
      { q: "How many digits does Qixingcai have?", a: "6 front digits plus 1 back digit — 7 in total. Front digits are 0-9; the back digit is 0-14." },
    ],
    related: [
      { label: "Browse draw history", path: "/data" },
      { label: "QXC frequency", path: "/qxc/frequency" },
      { label: "QXC rules", path: "/qxc/rules" },
    ],
    dataset: {
      name: "Qixingcai (QXC) historical results",
      description: "Historical China Sports Lottery Qixingcai records: draw number, date, 6 front digits and 1 back digit.",
      variableMeasured: ["Draw number", "Draw date", "Front digits", "Back digit"],
    },
  },
  "qxc-rules": {
    path: "/qxc/rules",
    game: "Qixingcai (QXC)",
    eyebrow: "QXC RULES",
    title: "Qixingcai Rules: Front Zone & Back Zone Explained",
    description:
      "Understand Qixingcai (QXC) rules — 6 front digits, 1 back digit, draw numbers and prize conditions. For rule reference and entertainment only.",
    summary:
      "A clear explanation of QXC's 6 front digits (0-9), 1 back digit (0-14), draw schedule and prize structure.",
    keyPoints: ["6 front digits, each 0-9", "1 back digit, range 0-14", "Prize rules per official announcement"],
    sections: [
      {
        heading: "Front zone and back zone",
        body:
          "Each QXC draw produces 6 front-zone digits (each 0-9) and 1 back-zone digit (0-14). The front zone is matched by position; the back zone is a single independent digit and should be shown separately.",
      },
      {
        heading: "Draw number and timing",
        body:
          "The draw number identifies a draw and the date confirms when it happened. QXC is usually drawn on Tuesday, Friday and Sunday; check number and date together.",
      },
      {
        heading: "Understanding prizes",
        body:
          "Prize tiers depend on how many front-zone digits match and whether the back zone matches — the top prize generally needs all 6 front digits plus the back digit. Actual names and amounts follow the official announcement.",
      },
    ],
    faq: [
      { q: "How many digits in one Qixingcai ticket?", a: "6 front digits plus 1 back digit — 7 in total." },
      { q: "Is the QXC back zone the same as the SSQ blue ball?", a: "No. The QXC back zone is a single 0-14 digit judged by QXC's own rules; the SSQ blue ball is 01-16 and is required for the jackpot." },
    ],
    related: [
      { label: "Rules overview", path: "/guide" },
      { label: "QXC results", path: "/qxc/results" },
      { label: "Prize calculator", path: "/jackpot" },
    ],
  },
};

export const seoTopicListEn = Object.values(seoTopicsEn);
