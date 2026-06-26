// AdSense 手动广告位（展示广告）slot ID 配置。
//
// 用法：在 AdSense 后台 →「广告」→「按广告单元」创建「展示广告」，
// 拿到形如 1234567890 的 data-ad-slot 数字，填到下面对应字段即可。
// 留空 "" 时该广告位不渲染、不占位、不影响页面；填上后自动生效。
//
// 注：此为「手动广告位」。若在 AdSense 后台开启了「Auto Ads（自动广告）」，
// Google 会另行自动插入广告，无需 slot ID（与此处可并存，但别过量铺设）。
export const AD_SLOTS = {
  homeBottom: "",     // 首页底部横幅（高流量，价值最高）
  generateBottom: "", // 模拟选号页底部（停留时间长）
  topicInContent: "", // SEO 专题页正文之后
};
