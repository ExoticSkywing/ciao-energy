# Ciao Energy 克隆验证记录

## 范围
- 项目：`/root/.hermes/profiles/frontend/workspace/ciao-energy`
- 目标站：`https://www.ciaoenergy.com`
- 历史上曾试用项目级通用提取器，现已移除；当前方法以 `web-clone` 的真源码/运行时证据流程为准。
- 浏览器统一复用 Hermes 共享 Chromium 缓存；未在项目中保留浏览器副本。

## 构建验证
命令：`npm run check`

结果：
- ESLint：通过
- TypeScript `tsc --noEmit`：通过
- Next.js 16.2.12 production build：通过
- 静态页面：`/` 与 `/_not-found`

## 运行验证
- Production preview：`next start --hostname 172.17.0.1 --port 3005`
- HTTP：`200`
- 桌面与移动端首屏均有产品罐，不是空白 WebGL。
- 移动端最终产品罐 Bounding Box：`x=126.35, y=211.70, w=137.30, h=275.53`（390×844），居中且未裁切。
- 右侧轮播箭头桌面 Bounding Box：`x=1365.13, y=414.72, w=48, h=48`。
- 右侧轮播箭头移动 Bounding Box：`x=326.61, y=362.91, w=40, h=40`。
- 菜单打开状态：通过（`.menu-panel.open`）。
- 口味切换：移动端实测从 `DOUBLE LITCHI` 切换为 `COCO CITRON VERT`，目标按钮 `aria-pressed=true`。
- FAQ 首项展开：通过（`.faq-item.open`）。
- Newsletter：演示模式，状态返回“Mode démonstration : aucune donnée n’a été envoyée.”；没有真实提交。
- Console errors：已完成的双视口自动化运行返回空数组。

## 视觉证据
- 原站移动全页：`docs/research/mobile/source-full.png`
- 克隆桌面 Hero：`docs/evidence/desktop-hero.png`
- 克隆移动 Hero：`docs/evidence/mobile-hero-final.png`

## 已知差异与诚实边界
- 原站核心是复杂 WebGL + GSAP/ScrollTrigger 体验；当前克隆优先覆盖首屏、区块结构、内容、关键交互和响应式完成路径。
- 当前产品视觉使用原站公开 UV 贴图和 CSS 罐体兜底，避免 WebGL/显卡不兼容时首屏黑屏；不是原站逐帧 3D 动画复制。
- 原仓库提取脚本对动画重站点 `load`/截图会超时，已在项目副本中改用 `commit` 并缩短滚动步数；没有修改上游仓库或全局 Skill。
- npm audit 报告 12 个 high severity 漏洞；未执行可能破坏依赖的 `npm audit fix --force`。
- 本任务达到“可运行、可交互、已真实验证的高保真原型”，不声称达到逐像素或逐帧完美复制。
