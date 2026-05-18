export const LOTTERY_META = {
  marksix: {
    key: "marksix",
    label: "六合彩",
    currencySymbol: "HK$",
    currencyName: "港币",
    dataSource: "数据来源：lottery.hk / 历史开奖数据库",
    statusSource: "数据来源：六合彩历史开奖数据",
    navSource: "数据源：六合彩历史开奖",
    drawSchedule: "每周二、四、六 21:30",
    drawTime: "21:30",
    drawWeekLabel: "周二 / 周四 / 周六",
    hasRollingPool: false,
    poolValueText: "固定奖金制",
    poolHintText: "六合彩为固定奖金制，不设滚动奖池",
    nextPoolText: "以官方公告为准",
    nextPoolHint: "固定奖金以当期派彩规则为准",
    prizeUnit: "单位：HK$",
    taxNote: "香港特区对彩票中奖奖金通常不征收个人所得税，实际以当地规定为准",
  },
  ssq: {
    key: "ssq",
    label: "双色球",
    currencySymbol: "¥",
    currencyName: "人民币",
    dataSource: "数据来源：500.com / 开奖公告数据",
    statusSource: "数据来源：双色球开奖公告数据",
    navSource: "数据源：双色球开奖公告",
    drawSchedule: "每周二、四、日 21:15",
    drawTime: "21:15",
    drawWeekLabel: "周二 / 周四 / 周日",
    hasRollingPool: true,
    poolValueText: "",
    poolHintText: "奖池金额以官方公告为准",
    nextPoolText: "以官方公告为准",
    nextPoolHint: "不展示非官方估算数据",
    prizeUnit: "单位：人民币",
    taxNote: "单注中奖金额超过 1 万元时，通常按 20% 税率缴纳个人所得税，实际以当地规定为准",
  },
};

export function getLotteryMeta(type) {
  return LOTTERY_META[type] || LOTTERY_META.marksix;
}
