import fs from "node:fs";
import assert from "node:assert/strict";
import { createFortuneResult } from "../src/utils/fortuneShake.js";

const component = fs.readFileSync(new URL("../src/components/DashboardPrizeStatusCard.vue", import.meta.url), "utf8");
const styles = fs.readFileSync(new URL("../src/style.css", import.meta.url), "utf8");

const marksix = createFortuneResult({ lotteryType: "marksix", nonce: 1, dateSeed: "2026-06-17" });
assert.equal(marksix.numbers.length, 3, "fortune result should show three lucky numbers");
assert.ok(marksix.numbers.every((n) => n.value >= 1 && n.value <= 49), "marksix lucky numbers should fit 1-49");
assert.ok(marksix.message.includes("\u8d22\u795e"), "fortune message should mention caishen");

const qxc = createFortuneResult({ lotteryType: "qxc", nonce: 2, dateSeed: "2026-06-17" });
assert.ok(qxc.numbers.every((n) => n.value >= 0 && n.value <= 14), "qxc lucky numbers should fit 0-14");

assert.match(component, /v62-fortune-widget/, "dashboard should render the fortune widget");
assert.match(component, /v62-caishen-avatar/, "dashboard should include a visible caishen avatar");
assert.match(component, /v62-fortune-coin/, "dashboard should render coin burst particles");
assert.match(component, /\u5e26\u7740\u624b\u6c14\u53bb\u6a21\u62df\u9009\u53f7/, "dashboard should link fortune result to generate page");
assert.match(component, /\u4e0d\u5f71\u54cd\u5f00\u5956\u7ed3\u679c/, "dashboard should keep entertainment disclaimer");
assert.match(styles, /@keyframes v62-fortune-coin-burst/, "coin burst animation should exist");
