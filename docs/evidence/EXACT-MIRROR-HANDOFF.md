# Ciao Energy 精确镜像交接

## 目标

以 `https://www.ciaoenergy.com` 当前公开部署代码和公开资产为依据，建立本地镜像；不再用近似 React/Three.js 场景伪装成 1:1。

## 已实现

- 镜像主页及三个法律页面。
- 镜像原站 Three.js 模型、六套产品贴图、HDR、加载视频、背景图、GSAP、Webflow 运行时、字体、图标和音效等公开资产。
- 原站 WebGL/Lenis/GSAP/ScrollTrigger/声音/FAQ/菜单代码保留。
- Next.js `/` 用全视口 iframe 承载 `/mirror/index.html`。
- 删除 Umami 分析脚本和 reCAPTCHA 动态加载。
- Newsletter 已变更为本地演示提交，不会向原站 Brevo 账户写数据。
- 为本地脚本执行和开场动画增加可恢复的 readiness fallback，避免长期黑屏。

## 关键路径

- `public/mirror/index.html`
- `public/mirror/vendor/`
- `src/app/page.tsx`
- `scripts/capture_exact_clone.py`
- `scripts/finalize_exact_clone.py`
- `scripts/qa_local_clone.py`

## 实际验证

- `npm run check`：ESLint、TypeScript、Next.js production build 全部通过。
- Camofox host-gateway reachability：HTTP 200。
- 本地浏览器证据：CSS 正常解析；Canvas 为非零的全屏 WebGL 画布；原始 GLB/HDR/纹理均通过本地路径加载；DOM 快照显示 Logo、菜单、FAQ、Newsletter 和 Footer。

## 已知边界

- 原站本身是远程 Webflow 部署及公共静态资产。该镜像适合本地研究、验证和内容替换；公开发布前必须确认品牌、字体、音效、图片、模型及其他素材授权。
- Hermes/Camoufox 的经典外链脚本加载行为与普通 Chromium 有差异，因此镜像内附带本地 GSAP ESM 引导和 CSS readiness fallback。
- 尚未得到用户的最终产品评审批准，不能自行宣称产品意义上的“完成”。
