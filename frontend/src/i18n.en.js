// 应用页 UI 英文词典（简→英，人工维护）。缺失的串会回退显示简体。
export const uiEn = {
  // NavBar
  "数据概览": "Overview",
  "号码统计": "Number Stats",
  "走势分析": "Trends",
  "组合分析": "Pairs",
  "模拟选号": "Number Picker",
  "对奖": "Check Ticket",
  "奖金分析": "Prizes",
  "历史记录": "History",
  "六合彩": "Mark Six",
  "双色球": "Shuangseqiu",
  "7星彩": "Qixingcai",
  "数据分析平台": "Data Analysis Platform",
  "彩种": "Lottery",

  // Footer — group titles
  "快速入口": "Quick Links",
  "数据说明": "Data Info",
  "专题入口": "Topics",
  "法律合规": "Legal",
  // Footer — links
  "常见问题": "FAQ",
  "规则说明": "Rules",
  "奖金规则": "Prize Rules",
  "数据方法": "Methodology",
  "六合彩开奖": "Mark Six Results",
  "六合彩频率": "Mark Six Frequency",
  "六合彩历史": "Mark Six History",
  "六合彩波色": "Mark Six Colours",
  "六合彩特码": "Mark Six Extra No.",
  "双色球开奖": "SSQ Results",
  "双色球历史": "SSQ History",
  "双色球蓝球": "SSQ Blue Ball",
  "双色球红球": "SSQ Red Ball",
  "遗漏统计": "Missing Stats",
  "双色球规则": "SSQ Rules",
  "关于我们": "About Us",
  "隐私政策": "Privacy Policy",
  "理性娱乐": "Responsible Play",
  // Footer — text
  "邮件订阅": "Newsletter",
  "支持弈彩持续维护": "Support YiCai",
  "专注开奖数据整理、历史统计与趋势复盘，帮助你更清楚地理解号码分布。":
    "Focused on organising draw data, historical statistics and trend review to help you better understand number distribution.",
  "用于数据整理、服务器成本与产品改进，不提供任何结果判断服务。":
    "Used for data work, server costs and product improvements. We provide no result-prediction service.",
  "接收开奖数据更新、月度统计摘要与产品通知，仅供数据分析与娱乐参考。":
    "Receive draw updates, monthly summaries and product news — for data reference and entertainment only.",
  "免责声明：本平台仅提供开奖数据的统计分析服务，所有内容仅供娱乐参考，不构成任何投注建议或诱导。 彩票中奖号码为随机产生，历史数据不能保证未来结果。请理性娱乐，切勿沉迷。":
    "Disclaimer: This platform only provides statistical analysis of public draw data. All content is for entertainment reference and does not constitute any betting advice or inducement. Winning numbers are random and historical data cannot guarantee future results. Please play responsibly and do not become addicted.",
  "访问本网站即表示您已年满18周岁，并同意我们的服务条款与隐私政策。":
    "By visiting this site you confirm you are at least 18 years old and agree to our Terms of Service and Privacy Policy.",
  "联系我们：": "Contact us:",

  // CookieConsent
  "🍪 关于 Cookie 与数据分析": "🍪 About Cookies & Analytics",
  "我们使用 Cookie 进行网站分析（Google Analytics）与广告展示（Google AdSense），用于改进网站并支持免费运营。不收集个人身份信息，你可以拒绝，不影响使用。":
    "We use cookies for site analytics (Google Analytics) and advertising (Google AdSense), to improve the site and keep it free. No personally identifiable information is collected; you may decline without affecting your use of the site.",
  "查看隐私政策": "View Privacy Policy",
  "拒绝": "Decline",
  "接受": "Accept",

  // NewsletterSignup
  "邮箱地址": "Email address",
  "输入邮箱，接收开奖与数据更新": "Enter your email for draw & data updates",
  "提交中": "Submitting",
  "订阅": "Subscribe",
  "订阅即同意接收弈彩邮件，可随时退订。详情见": "By subscribing you agree to receive YiCai emails; unsubscribe anytime. See",
  "隐私政策": "Privacy Policy",
  "请输入邮箱地址。": "Please enter your email address.",
  "这个邮箱已经订阅过开奖与数据更新。": "This email is already subscribed to draw and data updates.",
  "订阅成功，后续会收到弈彩的数据更新邮件。": "Subscribed! You will receive YiCai data update emails.",
  "暂时无法提交，请稍后再试。": "Unable to submit right now. Please try again later.",

  // PrizeChecker
  "对奖器": "Prize Checker",
  "{game}对奖器": "{game} Prize Checker",
  "对奖器 - 双色球、六合彩、7星彩中奖查询": "Prize Checker - Shuangseqiu, Mark Six & Qixingcai Winning Check",
  "输入你选的号码，自动对照开奖结果，查询命中几个号码、中了第几等奖。数据对照仅供娱乐参考，最终奖级与奖金以官方公告为准。":
    "Enter your numbers and automatically compare them with the draw to see how many matched and which prize tier you hit. For data reference and entertainment only; final tiers and amounts follow the official announcement.",
  "选择开奖期号，输入你选的号码，自动对照开奖结果，看命中几个、中了第几等奖。数据对照仅供娱乐参考，<strong>最终奖级与奖金以官方公告为准</strong>。":
    "Pick a draw, enter your numbers, and compare against the result to see how many matched and which prize tier you hit. For data reference and entertainment only; <strong>final tiers and amounts follow the official announcement</strong>.",
  "对照开奖期号": "Draw to check against",
  "加载中…": "Loading…",
  "第 {n} 期（{date}）": "Draw {n} ({date})",
  "开奖号码：": "Winning numbers:",
  "蓝球": "Blue ball",
  "后区": "Back zone",
  "特码": "Extra number",
  "红球": "red ball",
  "前区": "front zone",
  "选号": "pick",
  "你的号码（{label} {min}-{max}）": "Your numbers ({label} {min}-{max})",
  "，按位置": ", by position",
  "六合彩对奖只需填你选的 6 个号码；特码由开奖产生，系统会自动判断你是否命中。":
    "For Mark Six, just enter your 6 chosen numbers; the extra number is drawn, and the tool checks it automatically.",
  "请先选择开奖期号。": "Please select a draw first.",
  "请填写完整的 6 个{label}号码（{min}-{max}）。": "Please enter all 6 {label} numbers ({min}-{max}).",
  "{label}号码不能重复。": "{label} numbers cannot repeat.",
  "请填写{label}号码（{min}-{max}）。": "Please enter the {label} number ({min}-{max}).",
  "🎉 恭喜，命中 {name}": "🎉 Congratulations — {name}!",
  "未中奖": "No prize this time",
  "头奖": "Jackpot", "二奖": "2nd Prize", "三奖": "3rd Prize", "四奖": "4th Prize", "五奖": "5th Prize", "六奖": "6th Prize", "七奖": "7th Prize",
  "一等奖": "1st Prize", "二等奖": "2nd Prize", "三等奖": "3rd Prize", "四等奖": "4th Prize", "五等奖": "5th Prize", "六等奖": "6th Prize",
  "命中 {n} 个正码": "{n} main numbers matched",
  " + 特别号": " + extra number",
  "命中 {n} 个红球": "{n} red balls matched",
  " + 蓝球": " + blue ball",
  "前区命中 {n} 位": "{n} front digits matched",
  " + 后区": " + back zone",
  "具体奖金金额每期浮动，<strong>以官方公告为准</strong>。": "Exact prize amounts vary per draw; <strong>the official announcement prevails</strong>.",
  "7星彩奖级以官方奖级表为准。": "Qixingcai prize tiers follow the official prize table.",
  "本次未达到可中奖的命中条件。开奖结果具有随机性，仅供娱乐参考。": "Your numbers did not meet a winning condition this time. Draws are random; for entertainment reference only.",
  "免责声明：对奖器仅按公开规则做号码对照，方便你自查，<strong>不构成任何投注建议，最终中奖结果与奖金以官方公告为准</strong>。开奖结果具有随机性，请理性娱乐。":
    "Disclaimer: This tool only compares numbers using public rules to help you self-check. <strong>It is not betting advice; the final result and amounts follow the official announcement</strong>. Draws are random — please play responsibly.",

  // Shared section headings
  "常见问题": "FAQ",
  "常见问答": "FAQ",

  // About
  "关于弈彩 YiCai - 彩票开奖数据统计平台": "About YiCai - Lottery Draw Data & Statistics Platform",
  "弈彩 YiCai 是彩票开奖数据统计平台，介绍平台定位、各彩种数据来源、更新机制与合规免责说明。":
    "YiCai is a lottery draw data and statistics platform. Learn about our positioning, data sources for each game, update schedule and compliance disclaimer.",
  "弈彩 YiCai 是一个彩票开奖数据统计平台，提供六合彩、双色球、7星彩的历史开奖记录、号码频率、冷热遗漏与走势分析，内容仅供数据分析与娱乐参考。":
    "YiCai is a lottery draw data and statistics platform providing historical draw records, number frequency, hot/cold and missing stats and trend analysis for Mark Six, Shuangseqiu and Qixingcai. All content is for data reference and entertainment only.",
  "关于弈彩 YiCai": "About YiCai",
  "<strong>弈彩（YiCai）是一个彩票开奖数据统计平台</strong>，专注于开奖数据整理、历史记录、号码统计与走势分析。":
    "<strong>YiCai is a lottery draw data and statistics platform</strong> focused on organising draw data, historical records, number statistics and trend analysis.",
  "我们为用户提供清晰的号码分布、频率统计、冷热遗漏与走势分析等数据服务，帮助用户理解开奖数据的历史分布。弈彩仅提供数据整理与统计分析，<strong>不参与任何投注经营，也不提供任何投注或购彩渠道</strong>。":
    "We provide clear number distribution, frequency stats, hot/cold and missing data and trend analysis to help you understand the historical distribution of draw data. YiCai only organises data and runs statistical analysis; <strong>we do not operate any betting business and provide no betting or ticket-purchasing channel</strong>.",
  "数据来源": "Data Sources",
  "各彩种数据均整理自公开开奖资料；若与官方公告存在差异，请以官方公告为准：":
    "Data for each game is compiled from public draw information; if it differs from the official announcement, the official announcement prevails:",
  "<strong>六合彩：</strong>参考香港赛马会公开开奖资料（lottery.hk）整理。":
    "<strong>Mark Six:</strong> compiled with reference to the Hong Kong Jockey Club public draw data (lottery.hk).",
  "<strong>双色球：</strong>参考中国福利彩票开奖公告（500.com）整理。":
    "<strong>Shuangseqiu:</strong> compiled with reference to China Welfare Lottery draw announcements (500.com).",
  "<strong>7星彩：</strong>参考中国体育彩票开奖公告（500.com）整理。":
    "<strong>Qixingcai:</strong> compiled with reference to China Sports Lottery draw announcements (500.com).",
  "更新机制": "Update Schedule",
  "数据通常在每期开奖后同步整理。开奖时间因彩种而异（六合彩每周二、四、六；双色球每周二、四、日；7星彩每周二、五、日），具体更新时间受官方公告发布时间与数据同步状态影响。":
    "Data is usually organised after each draw. Draw days vary by game (Mark Six: Tue/Thu/Sat; Shuangseqiu: Tue/Thu/Sun; Qixingcai: Tue/Fri/Sun); the exact update time depends on when the official announcement is released and on data sync status.",
  "免责声明": "Disclaimer",
  "本平台所有内容仅供数据分析与娱乐参考。开奖结果具有随机性，历史数据不能保证或预示未来结果；号码统计、冷热、遗漏与走势分析均不构成任何参与建议。请理性娱乐，并以官方公告为准。":
    "All content on this platform is for data reference and entertainment only. Draws are random and historical data cannot guarantee or foretell future results; number statistics, hot/cold, missing and trend analysis do not constitute any participation advice. Please play responsibly, and the official announcement prevails.",
  "订阅数据更新": "Subscribe to Data Updates",
  "接收开奖数据更新与统计摘要，内容仅供数据分析与娱乐参考。":
    "Receive draw data updates and statistical summaries — for data reference and entertainment only.",

  // Strategy
  "数据分析方法说明": "About Our Data Analysis Methods",
  "介绍冷热号、遗漏、连号、区间分布、走势等数据分析指标的含义与边界。所有指标仅供数据分析与娱乐参考，不构成建议。":
    "Explains the meaning and limits of analysis metrics such as hot/cold numbers, missing values, consecutive numbers, zone distribution and trends. All metrics are for data reference and entertainment only and do not constitute advice.",
  "数据分析方法": "Data Analysis Methods",
  "弈彩的所有分析指标都建立在一个前提上：<strong>彩票开奖是随机事件，历史数据只能帮助理解分布，不能预测或保证未来结果</strong>。下列方法仅用于复盘和理解历史开奖，<strong>不构成任何参与建议</strong>。":
    "Every metric on YiCai rests on one premise: <strong>lottery draws are random events; historical data can only help you understand distribution and cannot predict or guarantee future results</strong>. The methods below are only for reviewing and understanding past draws and <strong>do not constitute any participation advice</strong>.",
  "常见的分析指标": "Common Analysis Metrics",
  "<strong>冷热号：</strong>统计各号码在历史开奖中的出现频率。热号是近期或长期出现较多的号码，冷号反之；过去表现不代表未来结果。":
    "<strong>Hot/Cold numbers:</strong> count how often each number appeared in past draws. Hot numbers appeared more recently or over the long run, cold numbers less so; past performance does not represent future results.",
  "<strong>遗漏：</strong>记录某号码距离上次出现间隔了多少期。遗漏只反映历史间隔，不会改变下一期的开奖概率。":
    "<strong>Missing values:</strong> record how many draws since a number last appeared. Missing values only reflect historical gaps and do not change the probability of the next draw.",
  "<strong>走势：</strong>把历次开奖号码按期排列观察分布变化。走势图是历史数据的可视化，不是结果走向的指示。":
    "<strong>Trends:</strong> arrange past draw numbers by draw to observe distribution changes. A trend chart is a visualisation of historical data, not an indication of where results are heading.",
  "<strong>连号统计：</strong>记录历史中连号出现的频率和模式。":
    "<strong>Consecutive numbers:</strong> record the frequency and patterns of consecutive numbers in history.",
  "<strong>区间分布：</strong>将号码分成多个区间，观察开奖号码在各区间的分布情况。":
    "<strong>Zone distribution:</strong> split numbers into zones and observe how drawn numbers distribute across them.",
  "<strong>奇偶比例：</strong>统计开奖号码中奇数和偶数的比例分布。":
    "<strong>Odd/Even ratio:</strong> count the ratio of odd to even numbers among drawn numbers.",
  "如何正确理解这些指标": "How to Interpret These Metrics Correctly",
  "以上指标都是对<strong>已发生</strong>开奖结果的统计描述，适合用于查询、复盘和理解号码分布，不能用来判断或预测下一期开奖。任何单期开奖都可能与历史分布不同。":
    "All the metrics above are statistical descriptions of draws that <strong>have already happened</strong>. They are suited to looking up, reviewing and understanding number distribution, not to judging or predicting the next draw. Any single draw may differ from the historical distribution.",
  "所有分析仅供数据分析与娱乐参考，请勿沉迷。理性娱乐，保持在自己的承受范围内。":
    "All analysis is for data reference and entertainment only — please do not become addicted. Play responsibly and stay within what you can afford.",
  "号码统计和冷热号能预测下一期吗？": "Can number statistics and hot/cold numbers predict the next draw?",
  "不能。号码统计、冷热号、遗漏和走势都是对历史开奖样本的描述，开奖结果具有随机性，历史数据不能预测或保证未来结果。":
    "No. Number statistics, hot/cold numbers, missing values and trends all describe historical draw samples. Draws are random, and historical data cannot predict or guarantee future results.",
  "遗漏值越大是不是越容易开出？": "Does a larger missing value mean a number is more likely to come up?",
  "不是。遗漏只表示某号码距离上次出现间隔了多少期，间隔长短不会改变下一期的开奖概率。":
    "No. A missing value only shows how many draws since a number last appeared; the size of that gap does not change the probability of the next draw.",
  "这些数据分析能作为参与建议吗？": "Can this data analysis be used as participation advice?",
  "不能。本页所有指标仅用于理解历史数据分布，不构成任何参与建议。请理性娱乐。":
    "No. Every metric on this page is only for understanding the historical data distribution and does not constitute any participation advice. Please play responsibly.",

  // Responsible
  "理性娱乐指南": "Responsible Play Guide",
  "彩票是娱乐不是投资。识别问题性赌博的信号，了解负责任的娱乐原则与求助渠道。":
    "Lottery is entertainment, not investment. Recognise the signs of problem gambling and learn the principles of responsible play and where to get help.",
  "重要提示": "Important Notice",
  "彩票是一种娱乐方式，而非赚钱手段。请务必理性娱乐，切勿沉迷。":
    "Lottery is a form of entertainment, not a way to make money. Please play responsibly and do not become addicted.",
  "健康娱乐原则": "Principles of Healthy Play",
  "<strong>设定预算：</strong>只为娱乐目的而参与，绝不动用必要的生活费用。":
    "<strong>Set a budget:</strong> take part only for entertainment, and never use money you need for living expenses.",
  "<strong>控制时间：</strong>不要让彩票影响您的正常工作和生活。":
    "<strong>Manage your time:</strong> don't let the lottery affect your normal work and life.",
  "<strong>接受输赢：</strong>把投注视为娱乐消费，中奖是惊喜，不中亦属正常。":
    "<strong>Accept wins and losses:</strong> treat it as entertainment spending — winning is a nice surprise, not winning is normal.",
  "<strong>拒绝借贷：</strong>绝不借钱参与，不影响正常家庭财务。":
    "<strong>Never borrow:</strong> never borrow money to take part, and don't disturb your family's finances.",
  "<strong>及时求助：</strong>如发现自己有投注问题，请及时寻求专业帮助。":
    "<strong>Seek help early:</strong> if you notice you have a gambling problem, seek professional help promptly.",
  "彩票可以当作投资吗？": "Can the lottery be treated as an investment?",
  "不可以。彩票应被视为娱乐消费，不应被当作投资、收入来源或财务计划。":
    "No. The lottery should be seen as entertainment spending, not as an investment, source of income or financial plan.",
  "怎样判断自己需要暂停？": "How do I know I need to take a break?",
  "如果购买彩票影响生活预算、工作休息或情绪状态，就应立即暂停并寻求家人或专业机构帮助。":
    "If buying lottery tickets affects your living budget, work and rest, or emotional state, you should stop immediately and seek help from family or a professional organisation.",
  "使用数据分析工具要注意什么？": "What should I keep in mind when using data analysis tools?",
  "数据分析只能帮助理解历史分布，不能保证未来结果，应始终保持娱乐心态。":
    "Data analysis can only help you understand historical distribution; it cannot guarantee future results. Always keep an entertainment mindset.",
  "未成年人可以使用弈彩吗？": "Can minors use YiCai?",
  "不可以。访问和使用本网站代表用户已年满18周岁，并理解彩票相关风险。":
    "No. Accessing and using this site means the user is at least 18 years old and understands the risks related to the lottery.",
  "如需帮助，请联系当地心理健康服务热线或相关戒赌机构。":
    "If you need help, please contact your local mental health hotline or a relevant gambling-support organisation.",

  // Privacy
  "弈彩 YiCai 的数据收集范围、Cookie 使用、第三方分析与广告（Google AdSense）说明、用户权利与联系方式。":
    "YiCai's scope of data collection, use of cookies, third-party analytics and advertising (Google AdSense), user rights and contact details.",
  "我们非常重视您的个人信息和隐私保护。": "We take the protection of your personal information and privacy very seriously.",
  "<strong>信息收集：</strong>我们仅收集您主动提供的信息，用于改善用户体验。我们不会收集您的财务信息或敏感个人信息。":
    "<strong>Information collection:</strong> we only collect information you actively provide, to improve your experience. We do not collect your financial information or sensitive personal information.",
  "<strong>Cookie使用：</strong>我们使用Cookie来记住您的偏好设置，如彩种选择等。":
    "<strong>Cookie use:</strong> we use cookies to remember your preferences, such as your chosen lottery game.",
  "<strong>第三方服务：</strong>我们使用 Google Analytics 等第三方分析服务来改进网站功能。":
    "<strong>Third-party services:</strong> we use third-party analytics services such as Google Analytics to improve the site.",
  "广告与第三方 Cookie：": "Advertising and third-party cookies: ",
  "本站使用 Google AdSense 等第三方广告服务。Google 及其合作伙伴会使用 Cookie，根据您过去对本站及其他网站的访问向您展示广告。您可以通过":
    "This site uses third-party advertising services such as Google AdSense. Google and its partners use cookies to serve ads based on your prior visits to this and other websites. You can manage or opt out of personalised ads via",
  "Google 广告设置": "Google Ads Settings",
  "管理或停用个性化广告，或访问": ", or visit",
  "退出第三方供应商的 Cookie。面向欧洲（EEA/英国）用户，本站提供 Cookie 同意选项（Consent Management Platform）。":
    "to opt out of third-party vendor cookies. For users in Europe (EEA/UK), this site provides a cookie consent option (Consent Management Platform).",
  "<strong>数据安全：</strong>我们采取合理的安全措施保护您的数据。":
    "<strong>Data security:</strong> we take reasonable security measures to protect your data.",
  "如有任何问题，请联系我们。": "If you have any questions, please contact us.",

  // Guide
  "双色球 & 六合彩玩法规则详解": "Shuangseqiu & Mark Six Rules Explained",
  "一文讲清双色球红蓝球玩法、六合彩 6+1 规则、各档奖项条件、开奖时间表与常见问答。":
    "A clear guide to Shuangseqiu red/blue ball play, the Mark Six 6+1 rules, prize-tier conditions, the draw schedule and common questions.",
  "玩法指南": "Game Guide",
  "双色球玩法": "Shuangseqiu (SSQ) Play",
  "双色球每注投注号码由6个红色球号码和1个蓝色球号码组成。红色球号码从01-33中选择6个，蓝色球号码从01-16中选择1个。":
    "Each Shuangseqiu entry is made up of 6 red ball numbers and 1 blue ball number. Pick 6 red balls from 01-33 and 1 blue ball from 01-16.",
  "香港六合彩玩法": "Hong Kong Mark Six Play",
  "香港六合彩每注投注号码由6个正码和1个特别号码组成。正码从01-49中选择6个，6个正码全中为头奖。":
    "Each Hong Kong Mark Six entry is made up of 6 main numbers and 1 extra number. Pick 6 main numbers from 01-49; matching all 6 main numbers is the jackpot.",
  "7星彩玩法": "Qixingcai (7-Star) Play",
  "7星彩每注号码按位置组成，前区6位从0-9中选择且允许重复，后区1位从0-14中选择。号码展示保留原始位置顺序，不排序、不去重。":
    "Each Qixingcai entry is arranged by position: 6 front digits chosen from 0-9 (repeats allowed) and 1 back digit chosen from 0-14. Numbers are shown in their original positional order, not sorted or de-duplicated.",
  "奖项设置": "Prize Tiers",
  "根据选中号码的数量和中奖情况，分为头奖、二奖、三奖等多个奖项。具体奖金金额以当期开奖公告为准。":
    "Based on how many numbers match and the winning conditions, prizes are split into multiple tiers such as jackpot, 2nd and 3rd prize. Exact amounts follow each draw's official announcement.",
  "双色球一注号码由哪些部分组成？": "What parts make up a single Shuangseqiu entry?",
  "双色球一注由6个红球和1个蓝球组成，红球范围为01-33，蓝球范围为01-16。":
    "A single Shuangseqiu entry consists of 6 red balls and 1 blue ball; red balls range 01-33 and the blue ball ranges 01-16.",
  "六合彩正码和特别号码有什么区别？": "What is the difference between Mark Six main numbers and the extra number?",
  "六合彩每期开出6个正码和1个特别号码，头奖只看6个正码，特别号码主要用于部分奖等条件。":
    "Each Mark Six draw produces 6 main numbers and 1 extra number. The jackpot looks only at the 6 main numbers; the extra number is mainly used for the conditions of certain lower tiers.",
  "弈彩的数据适合做什么？": "What is YiCai's data good for?",
  "弈彩用于查看历史开奖、号码频率、冷热遗漏和走势分布，所有内容仅供数据分析与娱乐参考。":
    "YiCai is for viewing historical draws, number frequency, hot/cold and missing stats and trend distribution. All content is for data reference and entertainment only.",
  "历史数据能保证未来结果吗？": "Can historical data guarantee future results?",
  "不能。彩票开奖具有随机性，历史数据只能帮助理解分布情况，不能保证未来结果。":
    "No. Lottery draws are random; historical data can only help you understand the distribution and cannot guarantee future results.",
  "开奖时间以哪里为准？": "Which draw time is authoritative?",
  "开奖时间与结果应以官方开奖公告为准，弈彩会尽量及时同步并整理展示。":
    "Draw times and results should follow the official draw announcement; YiCai syncs and presents them as promptly as it can.",

  // PatternsArticle
  "走势分析专题文章": "Trend Analysis Feature Article",
  "深度文章：连号现象、区间分布、和值统计等走势特征的统计学解读。基于历史数据的科普内容。":
    "In-depth article: a statistical reading of trend features such as consecutive numbers, zone distribution and sum statistics. Educational content based on historical data.",
  "模式分析文章": "Pattern Analysis Articles",
  "号码出现频率分析": "Number Frequency Analysis",
  "在彩票分析中，我们通常会统计每个号码在历史开奖中的出现频率。高频率号码被称为“热号”，低频率号码被称为“冷号”。然而，由于开奖的随机性，热号未必会在未来继续频繁出现，冷号也未必会继续保持低频率。":
    "In lottery analysis we usually count how often each number appears in past draws. High-frequency numbers are called “hot” and low-frequency ones “cold”. However, because draws are random, hot numbers will not necessarily keep appearing often, nor will cold numbers necessarily stay infrequent.",
  "连号现象研究": "Consecutive-Number Phenomenon",
  "连号是指开奖号码中存在两个或以上连续的数字。通过分析历史数据，我们可以统计连号出现的概率。但需要注意的是，每一次开奖都是独立事件，历史数据不能保证未来结果。":
    "Consecutive numbers means two or more adjacent digits among the drawn numbers. By analysing historical data we can count how often they occur. Note, though, that every draw is an independent event and historical data cannot guarantee future results.",
  "区间分布规律": "Zone Distribution Patterns",
  "将号码池划分为多个区间（如低区、中区、高区），统计开奖号码在各区间的分布情况。这种方法可以帮助我们了解号码的分散程度，仅供数据分析与娱乐参考。":
    "Split the number pool into zones (e.g. low, middle, high) and count how drawn numbers spread across them. This helps you understand how dispersed the numbers are — for data reference and entertainment only.",

  // Odds
  "双色球 & 六合彩中奖概率详解": "Shuangseqiu & Mark Six Winning Odds Explained",
  "详细计算各档奖项的中奖概率：双色球一等奖 1772 万分之一，二、三等奖详细说明。":
    "Detailed winning odds for each prize tier: the Shuangseqiu 1st prize is about 1 in 177 million, with 2nd and 3rd tiers explained in detail.",
  "中奖概率说明": "Winning Odds",
  "{name}各奖项的中奖条件与概率": "Winning conditions and odds for each {name} prize tier",
  "香港六合彩": "Hong Kong Mark Six",
  "奖项": "Prize", "中奖条件": "Winning condition", "概率": "Odds", "奖金": "Prize amount",
  "注：中奖概率为理论值，实际奖金由奖池金额和中奖注数决定。请理性娱乐，切勿沉迷。":
    "Note: winning odds are theoretical values; actual amounts depend on the prize pool and the number of winning entries. Please play responsibly and do not become addicted.",
  // Odds — conditions
  "6红+1蓝": "6 red + 1 blue", "6红": "6 red", "5红+1蓝": "5 red + 1 blue",
  "5红 或 4红+1蓝": "5 red, or 4 red + 1 blue", "4红": "4 red", "2红+1蓝": "2 red + 1 blue",
  "6个正码全中": "all 6 main numbers", "5个正码+特别号": "5 main + extra", "5个正码": "5 main numbers",
  "4个正码+特别号": "4 main + extra", "4个正码": "4 main numbers", "3个正码+特别号": "3 main + extra", "3个正码": "3 main numbers",
  "前区 6 位 + 后区全中": "all 6 front digits + back zone", "前区 6 位全中": "all 6 front digits",
  "前区任意 5 位 + 后区": "any 5 front digits + back zone", "前区任意 5 位": "any 5 front digits", "按官方规则匹配": "matched per official rules",
  // Odds — amounts
  "约500万-1000万": "approx. 5M-10M", "约10万-100万": "approx. 100K-1M", "约3,000": "approx. 3,000",
  "约200": "approx. 200", "约10": "approx. 10", "约5": "approx. 5",
  "彩池决定": "set by the pool", "约HK$10,000": "approx. HK$10,000", "约HK$640": "approx. HK$640",
  "约HK$320": "approx. HK$320", "约HK$130": "approx. HK$130", "约HK$30": "approx. HK$30",
  "以官方公告为准": "per official announcement", "浮动奖金": "variable amount", "固定或浮动奖金": "fixed or variable amount",
  // Odds — FAQ
  "中奖概率是什么意思？": "What do the winning odds mean?",
  "中奖概率是按号码组合总数计算出的理论比例，用于理解不同奖项的难度。":
    "Winning odds are theoretical ratios calculated from the total number of combinations, used to understand how hard each tier is.",
  "双色球一等奖概率是多少？": "What are the odds of the Shuangseqiu 1st prize?",
  "双色球一等奖需要6个红球和1个蓝球全部相符，理论概率约为1/177,210,888。":
    "The Shuangseqiu 1st prize requires all 6 red balls and 1 blue ball to match, with theoretical odds of about 1/177,210,888.",
  "六合彩头奖概率是多少？": "What are the odds of the Mark Six jackpot?",
  "六合彩头奖需要6个正码全部相符，理论概率约为1/13,983,816。":
    "The Mark Six jackpot requires all 6 main numbers to match, with theoretical odds of about 1/13,983,816.",
  "号码频率会改变单注概率吗？": "Does number frequency change the odds of a single entry?",
  "不会。频率统计反映历史分布，单期开奖仍是随机事件，单注理论概率不因历史频率而改变。":
    "No. Frequency statistics reflect the historical distribution; each draw is still a random event, and the theoretical odds of a single entry do not change with historical frequency.",
  "概率表可以用于什么场景？": "What is the odds table useful for?",
  "概率表适合理解奖项难度与规则差异，仅供数据分析与娱乐参考。":
    "The odds table is suited to understanding tier difficulty and rule differences — for data reference and entertainment only.",

  // JackpotAnalysis
  "双色球 & 六合彩奖金税务计算器": "Shuangseqiu & Mark Six Prize Tax Calculator",
  "输入中奖金额查看税后到手数额。双色球 20% 个税，香港六合彩免税，含各档奖项金额详解。":
    "Enter a prize amount to see the after-tax take-home figure. Shuangseqiu has 20% income tax, Hong Kong Mark Six is tax-free, with each prize tier explained.",
  "奖金分析": "Prize Analysis",
  "输入假设中奖金额，查看 {label} 在当前规则下的大致到手金额与税费拆解。":
    "Enter an assumed prize amount to see the approximate take-home figure and tax breakdown for {label} under the current rules.",
  "假设中奖金额": "Assumed prize amount",
  "输入金额": "Enter amount",
  "税务规则": "Tax rule",
  "个人所得税": "Personal income tax",
  "无税费": "No tax",
  "免税": "Tax-free",
  "到手金额拆解": "Take-home breakdown",
  "税前金额": "Pre-tax amount",
  "最终到手": "Final take-home",
  "金额占比": "Amount split",
  "到手": "Take-home",
  "税费": "Tax",
  "到手金额": "Take-home amount",
  "奖金税务常见问答": "Prize & Tax FAQ",
  "免责声明：奖金分析仅供参考，实际税率与规则以当地主管机构公布信息为准。":
    "Disclaimer: this prize analysis is for reference only; actual tax rates and rules follow information published by the local competent authority.",
  "港币": "HKD",
  "人民币": "CNY",
  "香港特区对彩票中奖奖金通常不征收个人所得税，实际以当地规定为准":
    "Hong Kong SAR generally does not levy personal income tax on lottery winnings; actual treatment follows local rules.",
  "单注中奖金额超过 1 万元时，通常按 20% 税率缴纳个人所得税，实际以当地规定为准":
    "When a single entry's winnings exceed CNY 10,000, personal income tax is generally levied at 20%; actual treatment follows local rules.",
  "双色球中奖奖金需要缴税吗？": "Are Shuangseqiu winnings taxed?",
  "中国内地彩票单注中奖金额超过规定门槛时通常需要缴纳个人所得税，页面计算仅作规则理解参考。":
    "On the Chinese mainland, single-entry lottery winnings above a set threshold are generally subject to personal income tax; the calculation here is only for understanding the rules.",
  "香港六合彩奖金是否需要缴税？": "Are Hong Kong Mark Six winnings taxed?",
  "香港六合彩奖金通常按香港本地规则处理，本页面以免税口径展示，实际以官方与当地规定为准。":
    "Hong Kong Mark Six winnings are generally handled under local Hong Kong rules; this page shows them as tax-free, but the official and local rules prevail.",
  "页面里的奖金金额一定准确吗？": "Are the prize amounts on the page always accurate?",
  "奖金会受奖池、中奖注数和官方公告影响，弈彩展示的计算结果仅供数据分析与娱乐参考。":
    "Prize amounts are affected by the pool, the number of winning entries and the official announcement; the figures YiCai shows are for data reference and entertainment only.",
  "税后金额怎么计算？": "How is the after-tax amount calculated?",
  "税后金额按输入金额扣除对应税率后估算，用于帮助理解不同彩票规则下的金额差异。":
    "The after-tax amount is estimated by deducting the applicable tax rate from the amount you enter, to help you understand how amounts differ across lottery rules.",

  // FrequencyAnalysis
  "双色球冷热号统计 & 六合彩号码频率分析": "Shuangseqiu Hot/Cold Stats & Mark Six Number Frequency",
  "实时统计号码在历史开奖中的出现频率、热号冷号排行、遗漏期数。数据仅供统计参考，不构成投注建议。":
    "Live statistics of how often numbers appear in past draws, hot/cold rankings and missing draws. For statistical reference only; not betting advice.",
  "数字出现频率、冷热分析与遗漏追踪": "Number frequency, hot/cold analysis and missing tracking",
  "{n}球": "{n} balls",
  "加载中...": "Loading...",
  "数字出现频率排名": "Number Frequency Ranking",
  "高频数字 (Top 10)": "Hot Numbers (Top 10)",
  "暂无数据": "No data yet",
  "出现 {n} 次": "appeared {n} times",
  "评分 {n}": "score {n}",
  "低频数字 (Bottom 10)": "Cold Numbers (Bottom 10)",
  "遗漏数字 (久未开出)": "Overdue Numbers (long unseen)",
  "遗漏 {n} 期": "missing {n} draws",
  "完整排名 ({label})": "Full Ranking ({label})",
  "排名": "Rank",
  "数字": "Number",
  "出现次数": "Appearances",
  "蓝球次数": "Blue ball count",
  "特别号次数": "Extra no. count",
  "遗漏期数": "Missing draws",
  "上次出现": "Last seen",
  "热度": "Heat",
  "趋势": "Trend",
  "已选": "Selected",
  "查看": "View",
  "数字 #{n} 近50期滚动频率": "Rolling frequency of #{n} over the last 50 draws",
  "点击表格中其他数字可切换": "Click another number in the table to switch",
  "关闭": "Close",

  // PairAnalysis
  "双色球 & 六合彩号码组合统计": "Shuangseqiu & Mark Six Number Pairing Stats",
  "统计两两号码同时出现的历史频次，发现号码组合规律。纯数据展示，不构成任何投注建议。":
    "Counts how often pairs of numbers appear together in history to reveal pairing patterns. Pure data display; not betting advice.",
  "数字组合分析": "Number Pairing Analysis",
  "探索数字之间的共现关系与最佳配对": "Explore co-occurrence relationships and best pairings between numbers",
  "数字选择器": "Number Selector",
  "点击数字查看其最佳配对": "Click a number to see its best pairings",
  "当前选中": "Selected",
  "与 #{n} 的最佳配对": "Best pairings with #{n}",
  "常见组合数字对 (Top 50)": "Most Common Number Pairs (Top 50)",
  "数字 A": "Number A",
  "数字 B": "Number B",
  "共现次数": "Co-occurrences",
  "配对分析概览": "Pairing Analysis Overview",
  "数字 #{n}": "Number #{n}",
  "共有 {n} 个与之配对的数字记录": "{n} numbers recorded as pairing with it",
  "最佳配对 Top 5": "Top 5 Pairings",
  "{n} 次": "{n} times",
  "选择数字查看详细配对": "Select a number to see detailed pairings",
  "点击上方数字球或左侧表格中的数字": "Click a number ball above or a number in the table on the left",

  // PatternAnalysis
  "双色球 & 六合彩走势分析 - 区间、奇偶、连号": "Shuangseqiu & Mark Six Trend Analysis - Zones, Odd/Even, Consecutive",
  "多维度走势分析：奇偶比、大小分布、连号特征、和值分布、号码区间走势。基于历史开奖数据的统计观察。":
    "Multi-dimensional trend analysis: odd/even ratio, big/small distribution, consecutive features, sum distribution and number-zone trends. Statistical observation based on historical draw data.",
  "奇偶、大小、连号、区间与总和分布统计": "Odd/even, big/small, consecutive, zone and sum distribution stats",
  "有连号": "With consecutive", "无连号": "No consecutive",
  "期数": "Draws", "出现次数": "Appearances",
  "奇数": "Odd", "偶数": "Even", "大数": "Big", "小数": "Small",
  "奇偶分布": "Odd/Even Distribution",
  "大小分布": "Big/Small Distribution",
  "连号统计": "Consecutive Numbers",
  "区间分布": "Zone Distribution",
  "总和分布": "Sum Distribution",
  "统计摘要": "Summary",
  "暂无走势分析数据": "No trend analysis data yet",

  // DataManagement
  "六合彩 & 双色球历史开奖记录查询": "Mark Six & Shuangseqiu Historical Draw Records",
  "完整收录香港六合彩、双色球历史开奖数据，支持按期数、日期、号码筛选查询。":
    "A complete archive of Hong Kong Mark Six and Shuangseqiu historical draw data, searchable by draw number, date and number.",
  "查看历史记录与数据更新": "View historical records and data updates",
  "共 {n} 条记录": "{n} records in total",
  "刷新中...": "Refreshing...",
  "更新数据": "Update data",
  "正在刷新数据...": "Refreshing data...",
  "数据已刷新": "Data refreshed",
  "刷新失败: ": "Refresh failed: ",
  "上一页": "Previous",
  "下一页": "Next",
  "第 {page} / {total} 页": "Page {page} / {total}",
  "更新日志": "Update Log",
  "暂无日志": "No logs yet",
  "时间": "Time",
  "来源": "Source",
  "状态": "Status",
  "获取": "Fetched",
  "新增": "Added",

  // DrawTable
  "特别号": "Extra no.",
  "期号": "Draw No.",
  "日期": "Date",
  "开奖数字": "Numbers",
  "单/双": "Odd/Even",
  "大小": "Big/Small",
  "总和": "Sum",
  "连号": "Consecutive",
  "暂无数据，请先导入数据": "No data yet — please import data first",
  "是": "Yes",

  // lotteryMeta (shared, displayed via t())
  "固定奖金制": "Fixed-prize system",
  "六合彩为固定奖金制，不设滚动奖池": "Mark Six uses a fixed-prize system with no rolling jackpot",
  "奖池金额以官方公告为准": "The pool amount follows the official announcement",
  "奖池滚存以官方公告为准": "Pool rollover follows the official announcement",
  "固定奖金以当期派彩规则为准": "Fixed prizes follow the payout rules for that draw",
  "不展示非官方估算数据": "We do not show unofficial estimated figures",
  "7星彩奖池与派彩数据以中国体育彩票公告为准": "Qixingcai pool and payout data follow China Sports Lottery announcements",
  "数据来源：lottery.hk / 历史开奖数据库": "Source: lottery.hk / historical draw database",
  "数据来源：500.com / 开奖公告数据": "Source: 500.com / draw announcement data",
  "数据来源：500.com / 中国体育彩票开奖公告": "Source: 500.com / China Sports Lottery draw announcements",
  "数据来源：六合彩历史开奖数据": "Source: Mark Six historical draw data",
  "数据来源：双色球开奖公告数据": "Source: Shuangseqiu draw announcement data",
  "数据来源：7星彩历史开奖记录": "Source: Qixingcai historical draw records",
  "周二 / 周四 / 周六": "Tue / Thu / Sat",
  "周二 / 周四 / 周日": "Tue / Thu / Sun",
  "周二 / 周五 / 周日": "Tue / Fri / Sun",
  "单位：HK$": "Unit: HK$",
  "单位：人民币": "Unit: CNY",
  "数据来源：": "Source: ",

  // Dashboard
  "弈彩 YiCai - 彩票开奖数据、号码统计与走势分析平台": "YiCai - Lottery Draw Data, Number Stats & Trend Analysis Platform",
  "弈彩 YiCai 提供彩票开奖数据、历史开奖记录、号码频率、冷热遗漏、走势分析与模拟选号。数据每期更新，仅供数据分析与娱乐参考。":
    "YiCai provides lottery draw data, historical records, number frequency, hot/cold and missing stats, trend analysis and a number simulator. Updated every draw — for data reference and entertainment only.",
  "近出": "recent",
  "热号 Top 6": "Hot Top 6", "近百期出现靠前": "Frequent in the last 100 draws",
  "冷号 Top 6": "Cold Top 6", "遗漏期数靠前": "Longest missing streaks",
  "回补观察": "Recovery watch", "最新开奖命中": "Hit in the latest draw",
  "连续活跃": "Consistently active", "综合热度较高": "High overall heat",
  "出现 {high} - {low} 次": "appeared {high} - {low} times",
  "以近期开奖为参考": "based on recent draws",
  "官方未公布": "Not yet announced",
  "下期估计头奖基金 · 香港赛马会": "Estimated next jackpot fund · HKJC",
  "本期销量 {amount}": "This draw's sales {amount}",
  "抓取中": "Fetching", "正在读取最新奖金与注数": "Reading the latest prizes and winning counts",
  "已更新": "Updated", "待公布": "Pending",
  "接口暂未返回真实奖金，先展示奖项规则": "The API has not returned real prize data yet; showing the prize rules for now",
  "开奖日期": "Draw date", "奖池": "Pool", "销售额": "Sales",
  "近期统计": "Recent stats", "最长遗漏 {n} 期": "Longest miss {n} draws", "以历史记录页为准": "see the history page",
  "等待最新开奖": "Awaiting the latest draw", "本期出现连号": "Consecutive numbers this draw", "本期未出现连号": "No consecutive numbers this draw",
  "一区": "Zone 1", "二区": "Zone 2", "三区": "Zone 3", "四区": "Zone 4",
  "前区 (0-4)": "Front (0-4)", "前区 (5-9)": "Front (5-9)", "后区 (0-14)": "Back (0-14)",
  "等待数据": "Awaiting data", "暂无近期开奖": "No recent draws", "分层参考": "Tiered reference",
  "{zone}偏热": "{zone} runs hot", "{range} · {count} 次": "{range} · {count} times", "{zone}回补观察": "{zone} recovery watch",
  "大小结构": "Big/small structure", "结构均衡": "Balanced", "轻微偏大": "Slightly big-heavy", "轻微偏小": "Slightly small-heavy",
  "分层选号参考": "Tiered pick reference",
  "6红 + 1蓝": "6 red + 1 blue", "5红 + 1蓝": "5 red + 1 blue", "5红 / 4红 + 1蓝": "5 red / 4 red + 1 blue",
  "4红 / 3红 + 1蓝": "4 red / 3 red + 1 blue", "中蓝 / 2红 + 1蓝": "blue / 2 red + 1 blue",
  "6个正码": "6 main", "5个正码 + 特别号": "5 main + extra", "5个正码": "5 main",
  "4个正码 + 特别号": "4 main + extra", "4个正码": "4 main", "3个正码 + 特别号": "3 main + extra", "3个正码": "3 main",
  "广告位 (AdSense)": "Ad slot (AdSense)",
  "广告 Advertisement": "Advertisement",

  // DashboardPrizeStatusCard
  "最新头奖": "Latest jackpot", "下一期头奖": "Next jackpot", "奖金说明": "Prize info",
  "开奖时间": "Draw time", "香港赛马会": "HKJC",
  "香港六合彩 · Mark Six": "Hong Kong Mark Six", "中国七星彩 · QXC": "China Qixingcai · QXC", "中国双色球 · SSQ": "China Shuangseqiu · SSQ",
  "开奖数据": "Draw Data", "彩票数据": "Lottery Data", "从容掌握": "at a glance",
  "专业、透明、实时的双色球数据统计平台。每一期开奖，皆是概率与优雅的交汇。":
    "A professional, transparent, real-time Shuangseqiu data platform. Every draw is where probability meets elegance.",
  "专业、透明、实时的开奖数据统计平台。每一期开奖，皆是概率与优雅的交汇。":
    "A professional, transparent, real-time draw-data platform. Every draw is where probability meets elegance.",
  "6 红 + 1 蓝全中为一等奖": "Matching 6 red + 1 blue wins the 1st prize",
  "6 个正码全中为头奖，特别号用于部分奖项": "Matching all 6 main numbers wins the jackpot; the extra number applies to some tiers",
  "平时每 30 分钟同步，开奖夜 21:00-22:50 加密同步": "Synced every 30 min normally, and more frequently on draw nights 21:00-22:50",
  "{date} · 已开奖": "{date} · drawn",
  "查看开奖详情": "View draw details",
  "财神摆一下，生成娱乐手气签": "Shake the fortune god to generate a fun luck draw",
  "财神摆一下": "Shake for luck", "轻点试手气": "Tap to try your luck", "今日手气签": "Today's luck draw",
  "带着手气去模拟选号": "Take your luck to the simulator", "仅供娱乐，不影响开奖结果": "For fun only; does not affect the draw",
  "第 {n} 期": "Draw {n}",
  "玩法规则": "Rules", "更新频率": "Update frequency",
  "香港赛马会官方公开数据同步": "Synced from HKJC official public data", "500.com / 官方公开数据同步": "500.com / synced from official public data",
  "Next Draw · 下期开奖": "Next Draw",

  // DashboardNextDrawCard
  "下一期开奖": "Next Draw",
  "{week} {time} 开奖。距离第 {n} 期还有：": "Draw on {week} at {time}. Time until draw {n}:",
  "♧ 仅供参考，请以官方公布为准": "♧ For reference only; the official announcement prevails",
  "本期数据状态 · Status": "This Draw's Status",
  "数据完整性": "Data completeness", "49/49 号码已归档": "49/49 numbers archived", "33+16 号码已归档": "33+16 numbers archived",
  "头奖 / 奖池": "Jackpot / Pool", "同步频率": "Sync frequency",
  "LIVE · 系统正常": "LIVE · system normal",

  // DashboardStatusBar
  "仅供娱乐参考，不构成任何投注建议。": "For entertainment reference only; not any betting advice.",
  "最近开奖： {date} {time}": "Latest draw: {date} {time}",

  // DashboardDistributionCard
  "红球热度": "Red ball heat", "蓝球热度": "Blue ball heat",
  "红波热度": "Red heat", "蓝波热度": "Blue heat", "绿波热度": "Green heat",
  "号码热度全景": "Number Heat Overview",
  "统计近 24 期号码出现频率，热度越高颜色越深。": "Counts number frequency over the last 24 draws; hotter numbers are darker.",
  "热度说明": "Heat legend", "低频": "Low", "高频": "High", "24期累计数据": "24-draw cumulative",
  "次数": "Count", "占比": "Share", "最热号码": "Hottest numbers",
  "号码 {num} · 近24期出现 {count} 次 · 遗漏 {miss}": "Number {num} · appeared {count} times in 24 draws · missing {miss}",
  "{n}次": "{n}x",
  "红波 / 红球": "Red / Red ball", "蓝波 / 蓝球": "Blue / Blue ball", "绿波": "Green",
  "当期开奖": "This draw", "下方数字 = 近24期出现次数": "Number below = appearances in 24 draws", "详细统计 →": "Detailed stats →",

  // DashboardPrizeTableCard
  "开奖结算状态": "Settlement Status", "条件": "Condition", "注数": "Winners", "每注奖金": "Per-winner prize",

  // DashboardTrendGuideCard
  "分区结构走势": "Zone Structure Trend",
  "近 20 期分区占比 · 用于辅助分层选号": "Zone shares over the last 20 draws · to assist tiered picking",
  "等待近期开奖数据": "Awaiting recent draw data",
  "每根柱代表一期正码结构，颜色占比越高表示该区号码越集中。": "Each bar is one draw's main-number structure; a larger colour share means numbers cluster in that zone.",
  "近 20 期分区汇总": "20-draw zone summary", "按正码统计": "by main numbers",
  "最近 5 期结构": "Last 5 draws' structure", "快速复盘": "Quick review", "暂无结构": "No structure",
  "结构判断": "Structure read", "套入漏斗": "Apply to funnel", "选号落点": "Pick focus",
  "先用分区偏热/回补判断大方向，再回到分层选号用 10 → 8 → 6 收敛。":
    "First read the broad direction from hot/recovery zones, then go back to tiered picking and narrow down with 10 → 8 → 6.",

  // GenerateNumbers — SEO & FAQ
  "模拟选号器 - 随机选号、热号与遗漏选号工具（娱乐参考）": "Number Simulator - Random, Hot & Missing Picker (for fun)",
  "免费在线模拟选号器：热号优先、加权随机、追遗漏、分层漏斗 4 种娱乐型选号方式，覆盖双色球、7星彩等玩法。内容仅供娱乐参考，不构成任何投注建议。":
    "Free online number simulator: 4 fun strategies — hot-first, weighted random, chase-missing and tiered funnel — covering Shuangseqiu, Qixingcai and more. For entertainment reference only; not any betting advice.",
  "弈彩模拟选号器": "YiCai Number Simulator",
  "弈彩模拟选号器，提供热号优先、加权随机、追遗漏、分层漏斗 4 种娱乐型模拟选号方式，覆盖双色球、7星彩等玩法。仅供娱乐参考，不构成任何投注建议。":
    "The YiCai number simulator offers 4 fun strategies — hot-first, weighted random, chase-missing and tiered funnel — covering Shuangseqiu, Qixingcai and more. For entertainment reference only; not any betting advice.",
  "模拟选号器能预测中奖号码吗？": "Can the number simulator predict winning numbers?",
  "不能。本工具只是按热号、随机、遗漏等历史统计维度生成模拟号码，仅供娱乐参考，开奖结果具有随机性，任何选号都不构成参与建议。":
    "No. This tool only generates simulated numbers along historical statistical dimensions such as hot numbers, randomness and missing values. It is for entertainment only; draws are random and no pick constitutes participation advice.",
  "有哪几种模拟选号方式？": "What simulation methods are there?",
  "提供热号优先、加权随机、追遗漏、分层漏斗 4 种娱乐型方式，分别从不同的历史统计角度生成号码组合。":
    "There are 4 fun methods — hot-first, weighted random, chase-missing and tiered funnel — each generating combinations from a different historical-statistics angle.",
  "支持哪些彩种？": "Which lotteries are supported?",
  "支持双色球（6 红 + 1 蓝）、7 星彩（前区 6 位 + 后区 1 位）等玩法，可在页面顶部切换彩种。":
    "It supports Shuangseqiu (6 red + 1 blue), Qixingcai (6 front digits + 1 back digit) and more; switch lottery at the top of the page.",

  // GenerateNumbers — UI
  "{label} 模拟选号": "{label} Number Simulator",
  "按位置热度、历史频率、遗漏和后区候选生成可重复数字组合，适合做娱乐型观察。":
    "Generates repeatable digit combinations from positional heat, historical frequency, missing values and back-zone candidates — good for casual observation.",
  "按历史分布、冷热程度和分层条件生成模拟组合，适合做娱乐型筛选和走势对照。":
    "Generates simulated combinations from historical distribution, hot/cold levels and tiered conditions — good for casual filtering and trend comparison.",
  "以历史数据做模拟组合，不展示任何官方推荐。": "Builds simulated combinations from historical data; shows no official recommendation.",
  "固定奖金玩法同样只适合做模拟组合与走势观察。": "Fixed-prize games are also only suited to simulated combinations and trend observation.",
  "基础策略": "Basic strategies",
  "热号优先": "Hot first", "选近期与历史频率都偏高的号码": "Pick numbers that are frequent both recently and historically",
  "加权随机": "Weighted random", "按热度权重抽取，保留随机性": "Draw by heat weighting while keeping randomness",
  "追遗漏": "Chase missing", "挑选近期较久未出现的号码": "Pick numbers that have not appeared for a while",
  "进阶策略 · 推荐": "Advanced strategy · recommended",
  "分层筛选漏斗": "Tiered Filter Funnel",
  "综合冷热 / 走势 / 统计逐步精选，自动给出多组 6 号推荐": "Combines hot/cold, trends and stats to refine step by step, auto-suggesting several 6-number sets",
  "智能推荐": "Smart pick", "✓ 已选": "✓ Selected", "点击使用 →": "Click to use →",
  "按 6 个位置分别筛选 0-9，再独立筛选后区 0-14，保留位置与重复数字。":
    "Filters 0-9 for each of the 6 positions, then filters the back zone 0-14 separately, keeping positions and repeated digits.",
  "每位 10 → {p1} → {p2} → {p3} 个 · 输出最多 {n} 组": "Per digit 10 → {p1} → {p2} → {p3} · up to {n} sets",
  "漏斗：49 → {p1} → {p2} → {p3} 个 · 输出最多 5 组 6 号推荐": "Funnel: 49 → {p1} → {p2} → {p3} · up to 5 six-number sets",
  "第一步（{p1}）不能小于第二步（{p2}）": "Step 1 ({p1}) cannot be smaller than step 2 ({p2})",
  "第二步（{p2}）不能小于第三步（{p3}）": "Step 2 ({p2}) cannot be smaller than step 3 ({p3})",
  "七星彩每位最终候选不能少于 1 个": "Each Qixingcai position must keep at least 1 final candidate",
  "最终号码数不能少于 6 个": "The final number count cannot be fewer than 6",
  "分层筛选配置": "Tiered Filter Settings", "先调核心 4 项，进阶选项可保持默认": "Adjust the 4 core items first; advanced options can stay default",
  "核心": "Core", "必填配置": "Required settings",
  "历史回顾期数": "History lookback", "看多少期历史来判断冷热": "How many past draws to judge hot/cold",
  "近 10 期": "Last 10", "近 30 期": "Last 30", "近 50 期（推荐）": "Last 50 (recommended)", "近 100 期": "Last 100", "近 200 期": "Last 200",
  "近 20 期": "Last 20", "近 50 期": "Last 50",
  "热号个数": "Hot count", "每个位置优先保留的热数字": "Hot digits kept first for each position", "出现频率最高的 N 个": "The N most frequent",
  "冷号个数": "Cold count", "每个位置纳入的冷数字": "Cold digits included for each position", "最久没出现的 N 个": "The N longest unseen",
  "剩余 {n} 个名额会由次热号补齐": "The remaining {n} slots are filled by next-hottest numbers",
  "漏斗步数": "Funnel steps",
  "每个位置独立压缩数字池，保留重复和位置顺序": "Each position compresses its own pool, keeping repeats and order",
  "三步逐步压缩号码池，最终保留 N 个作为推荐组合源": "Compresses the pool in three steps, keeping N as the recommendation source",
  "每位 10": "Per digit 10",
  "第一层/每位": "Tier 1 / pos", "第二层/每位": "Tier 2 / pos", "最终/每位": "Final / pos", "输出组数": "Output sets",
  "第一步保留": "Keep at step 1", "第二步保留": "Keep at step 2", "最终保留": "Keep at final",
  "✓ 每位最终池 {n} 个数字，按位置生成 {count} 组可重复组合": "✓ {n} digits per final pool; generates {count} repeatable combinations by position",
  "✓ 最终池 {n} 个号码，将自动产生多组 6 选组合推荐": "✓ {n} numbers in the final pool; multiple 6-number sets will be generated automatically",
  "最终池 6 个号码 = 单组推荐；调大可获多组组合": "A 6-number final pool = one set; increase it for multiple combinations",
  "进阶": "Advanced", "高级筛选条件": "Advanced filters", "（走势、奇偶、大小、和值、胆码、杀号）": "(trend, odd/even, big/small, sum, must-include, exclude)",
  "近期走势期数": "Recent trend window",
  "连号要求": "Consecutive rule", "不限": "Any", "偏好出现在连号场次的号": "Prefer numbers from draws with consecutives", "偏好出现在无连号场次的号": "Prefer numbers from draws without consecutives",
  "奇偶偏好": "Odd/even preference", "偏奇": "More odd", "偏偶": "More even", "奇偶平衡": "Balanced odd/even",
  "大小偏好": "Big/small preference", "偏大（5-9）": "More big (5-9)", "偏大（>24）": "More big (>24)", "偏小（0-4）": "More small (0-4)", "偏小（≤24）": "More small (≤24)", "大小平衡": "Balanced big/small",
  "和值下限": "Sum min", "和值上限": "Sum max", "前 6 位和值，不限": "Sum of first 6 digits, any",
  "胆码（必含）": "Must include", "0-9 数字，最多 3 个，系统会分配到位置池": "Digits 0-9, up to 3; assigned to position pools", "最多 3 个，逗号或空格分隔": "Up to 3, separated by comma or space",
  "例如：0, 7, 9": "e.g. 0, 7, 9", "例如：7, 23, 45": "e.g. 7, 23, 45",
  "杀号（必排）": "Exclude", "0-9 数字，所有位置都会排除": "Digits 0-9, excluded from all positions", "逗号或空格分隔": "Separated by comma or space",
  "例如：1, 3, 6": "e.g. 1, 3, 6", "例如：1, 13, 26": "e.g. 1, 13, 26",
  "重置": "Reset", "筛选中...": "Filtering...", "运行分层漏斗": "Run tiered funnel",
  "胆码最多 3 个": "At most 3 must-include numbers", "热号个数 + 冷号个数不能超过第一步保留个数": "Hot count + cold count cannot exceed the step-1 keep count", "调用失败": "Request failed",
  "生成组数": "Sets to generate", "当前策略：{label}": "Current strategy: {label}",
  "生成中...": "Generating...", "再来一次": "Again", "生成组合": "Generate",
  "七星彩位置漏斗": "Qixingcai Positional Funnel", "每一位独立筛选 0-9，保留位置顺序与重复数字。": "Each position filters 0-9 independently, keeping order and repeated digits.",
  "近 {n} 期开奖": "Last {n} draws", "第 {n} 位候选": "Position {n} candidates",
  "热": "Hot", "冷": "Cold", "补": "Fill",
  "{label}候选": "{label} candidates", "后区从 0-14 独立筛选，不参与前 6 位去重。": "The back zone is filtered 0-14 independently and is not de-duplicated with the first 6 digits.",
  "推荐": "Pick", "候选": "Candidates",
  "位置组合": "Positional combinations", "前 6 位可重复，后区独立生成；每组保留原始位置顺序。": "The first 6 digits may repeat and the back zone is generated separately; each set keeps the original order.", "专用漏斗": "Dedicated funnel",
  "和值": "Sum", "重复": "Repeats", "跨度": "Span",
  "大底筛选": "Base filter", "49 → {n} 个": "49 → {n}", "热 {h} · 冷 {c} · 补 {s}": "Hot {h} · cold {c} · fill {s}",
  "▼ 走势精选，淘汰 {a} 个中的 {b} 个": "▼ Trend refine: drop {b} of {a}",
  "走势精选": "Trend refine", "{a} → {b} 个": "{a} → {b}", "个": "",
  "淘汰：": "Dropped: ", "▼ 综合得分精选，淘汰 {n} 个": "▼ Composite-score refine: drop {n}",
  "最终号码池": "Final number pool",
  "推荐组合": "Recommended sets", "从最终池按综合得分排出 Top {n} 组": "Top {n} sets from the final pool by composite score",
  "（6 红 + 1 蓝）": "(6 red + 1 blue)", "6 号（红色为主号）": "6 numbers (red as main)", "分层漏斗": "Tiered funnel",
  "得分 {n}": "Score {n}", "没有符合和值范围的组合，请放宽和值过滤。": "No combinations match the sum range; please widen the sum filter.",
  "蓝球推荐（头奖必含）": "Blue ball pick (required for jackpot)", "特码辅助参考": "Extra number reference",
  "仅供参考": "Reference only", "6红+1蓝=一等奖": "6 red + 1 blue = 1st prize",
  "蓝球与红球独立开奖，按近期出现频次排序": "The blue ball is drawn independently of the red balls, sorted by recent frequency",
  "特码不影响头奖，按近期出现频次排序": "The extra number does not affect the jackpot, sorted by recent frequency",
  "推荐：": "Pick: ", "其他候选：": "Other candidates: ",
  "分析范围：近 {n} 期开奖": "Analysis range: last {n} draws",
  "特码辅助：": "Extra number: ", "（仅供参考，不影响头奖）": "(reference only; does not affect the jackpot)",
  "频次 {n}": "Freq {n}", "最近出现": "Recently seen",
  "选择策略，点击生成": "Choose a strategy and click generate",
  "系统会根据所选策略生成模拟号码，并显示对应的历史频次与遗漏情况。": "The system generates simulated numbers by the chosen strategy and shows each number's historical frequency and missing values.",
  "关于模拟选号": "About the Simulator",
  "模拟选号器把历史开奖数据当作样本，按不同统计维度生成号码组合，<strong>仅供娱乐参考</strong>。开奖结果具有随机性，任何方式都不能预测或保证结果。":
    "The simulator treats historical draw data as a sample and builds combinations along different statistical dimensions — <strong>for entertainment only</strong>. Draws are random and no method can predict or guarantee results.",
  "偏向近期与历史出现频率较高的号码，便于观察热号分布。": "Leans toward numbers frequent recently and historically, to observe the hot-number distribution.",
  "在随机基础上结合历史频率加权，兼顾随机性与样本分布。": "Adds historical-frequency weighting on top of randomness, balancing randomness and sample distribution.",
  "偏向遗漏期数较长的号码，仅用于复盘遗漏分布，不代表会回补。": "Leans toward numbers with longer missing streaks — only for reviewing the missing distribution, not implying they will return.",
  "按区间分层逐步收敛，演示一种结构化的号码组合思路。": "Narrows down through zone tiers step by step, demonstrating a structured way to build combinations.",
  "按彩种查看选号与开奖": "Pick & results by lottery",
  "双色球模拟选号": "Shuangseqiu simulator", "7星彩模拟选号": "Qixingcai simulator", "六合彩模拟选号": "Mark Six simulator",
  "双色球开奖结果": "Shuangseqiu results", "7星彩开奖结果": "Qixingcai results", "六合彩开奖结果": "Mark Six results",
  "免责声明：模拟选号仅供娱乐参考，不构成任何参与建议。彩票开奖结果具有随机性，历史数据不能保证未来结果。":
    "Disclaimer: the simulator is for entertainment reference only and does not constitute any participation advice. Lottery draws are random and historical data cannot guarantee future results.",
};
