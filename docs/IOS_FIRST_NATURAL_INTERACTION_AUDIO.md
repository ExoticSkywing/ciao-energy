# 首次自然交互解锁 iOS 站点音效：Ciao Energy 实战方法论

## 结论

移动端沉浸式站点不必强迫用户点击专用“开启声音”按钮。更自然、且已在真实 iPhone 环境通过人工验收的合同是：

```text
第一次自然交互开始
→ 不要求立即出声
→ 用户正常完成点击或滑动
→ 在可信的完成端点（本项目为 touchend）只恢复全局音频会话
→ 从第二次交互起，既有业务音效全部正常工作
```

三个关键词：**首次、自然、完成**。

- **首次**：授权只做一次，成功后移除监听器。
- **自然**：借用用户本来就会做的交互，不增加弹窗或教学步骤。
- **完成**：在浏览器更容易识别为明确意图的事件终点授权，而不是把 `touchstart` 一概当成许可。

## 最终 UX 合同

```text
首次横滑：完成 Carousel 操作，允许无声，同时在 touchend 解锁声音。
首次纵滑：完成页面滚动，允许无声，同时在 touchend 解锁声音。
第二次及以后：Carousel、滚动、Benefits、菜单、FAQ 继续使用原有语义音效。
```

用户不需要理解媒体策略，也不需要离开主任务寻找声音按钮。第一次无声还能避免突兀；用户参与体验后，声音自然加入。

## 核心架构：授权与播放分离

错误模型：

```text
首次手势 → 解锁 → 判断方向 → 立即播放某个音效
```

它会引入方向判断、重复播放、异步时序和业务耦合。

正确模型：

```text
授权层：第一次完整自然交互只执行 AudioContext.resume()
播放层：Carousel / Lenis / Benefits / Menu 各自继续拥有语义音效
```

声音授权是基础设施；声音播放是业务语义。两者必须分离。

## 最小实现

```js
let ctx = null;
let unlocked = false;

function initAudioContext() {
  if (!ctx) {
    ctx = new (window.AudioContext || window.webkitAudioContext)();
  }
}

function unlockAfterFirstCompletedGesture(event) {
  initAudioContext();

  const resume =
    ctx.state === 'suspended'
      ? ctx.resume()
      : Promise.resolve();

  Promise.resolve(resume).then(() => {
    unlocked = ctx.state === 'running';

    if (unlocked) {
      window.removeEventListener(
        'touchend',
        unlockAfterFirstCompletedGesture,
        true,
      );
    }
  });
}

window.addEventListener(
  'touchend',
  unlockAfterFirstCompletedGesture,
  { passive: true, capture: true },
);
```

播放函数保持单一门禁：

```js
function play(name) {
  if (!ctx || !unlocked || isMuted() || !buffers[name]) return;

  const source = ctx.createBufferSource();
  source.buffer = buffers[name];
  source.connect(ctx.destination);
  source.start(0);
}
```

既有回调不变：

```js
carousel.changed.connect(() => play('change'));
lenis.on('scroll', () => enteredNextSection && play('enter'));
benefitChanged.connect(() => play('benefits'));
menuButton.addEventListener('click', () => play('click'));
```

## 为什么 touchend 比 touchstart 更可靠

`touchstart` 只说明手指落下，后续可能是点击、滚动、横滑、长按、系统返回手势或误触。部分 iOS Safari/WKWebView 环境不会将它视为明确的媒体播放意图。

`touchend` 表示一次真实交互已经完成，意图边界更清晰，也更接近已被设备证明有效的按钮 `click` 终点。

因此不能抽象地说“任何触摸都能解锁声音”。正确说法是：

> 找到当前浏览器容器实际认可的可信完成端点，在该调用链中只恢复音频会话。

## “按钮有效”必须先消歧

“点击左右按钮后有声音”可能指 Carousel 箭头：

```text
.carousel_arrow.is-prev / .is-next
→ trusted click
→ previous()/next()
→ carousel.changed
→ play('change')
```

它不同于 Navbar 的 ON/OFF 状态。后者可能只更新视觉标签和波形，不代表媒体授权本身。

研究前必须记录：

- 用户实际点击的是哪个元素；
- 成功事件是 `click`、`touchend` 还是别的事件；
- 调用链里何时发生 `resume()` 或 `play()`；
- 声音是本次点击就响，还是从下一次手势开始响；
- Navbar ON/OFF 是否真的变化。

不得用含糊的“按钮”直接推断实现路径。

## 失败路线与原因

### 1. 在 touchstart 同时解锁并播放

`touchstart` 可能只是滚动、长按或系统手势的开始；在部分 Safari/WKWebView 中并不等价于明确播放意图。即便回调执行，真实设备也可能保持静音。

### 2. 等待方向判断后再播放

```text
touchstart → touchmove → 判断方向 → CustomEvent → play()
```

链路越长，越可能脱离用户激活窗口；还会与 Carousel `changed`、Lenis section 事件重复播放。

### 3. 等 Carousel 或滚动事件首次解锁

Carousel 和 Lenis 回调属于业务状态通知，不保证仍处于浏览器认可的原始用户手势调用栈。它们适合授权后的播放，不适合承担首次授权。

### 4. 模拟按钮 click

```js
button.click();
```

程序化点击的 `isTrusted` 为 `false`，不能复制真实点击的用户激活。所谓“模拟按钮”，应该复用内部函数，而不是合成 DOM 事件。

### 5. 复制其他站点的声音控制器

Three.js Punk 使用顶级 HTTPS 文档、长循环环境音和直接 `<audio>.play()`。复制其代码到 HTTP IP、iframe 或 Telegram/WKWebView 容器，并不意味着媒体策略等价。必须同时审计协议、宿主、媒体类型和事件端点。

### 6. 用自动化标记代替人耳验收

CDP/Playwright 合成触摸可能触发 JavaScript，却不产生真实 `userActivation`。`data-audio-unlocked=true`、Context 状态或构建成功都不能证明真实 iPhone 发出了声音。

## 诊断优先级

```text
真实 iPhone 人耳验收
> 同设备浏览器事件与 Context 状态
> Safari/WKWebView 容器与协议
> 自动化交互回归
> 源码理论推断
```

真实设备报告“无声”时，候选立即失败；不得用自动化结果覆盖。

## 环境审计清单

在迁移到其他项目时记录：

- 顶级文档、iframe、object 还是 WKWebView；
- HTTPS 域名还是 HTTP IP；
- Safari、Telegram 内置浏览器还是其他 App WebView；
- `event.type`、`event.isTrusted`；
- `navigator.userActivation.isActive/hasBeenActive`；
- `AudioContext.state` 在 resume 前后是否为 `running`；
- `resume()` 或 `play()` 的拒绝名称；
- 首次交互是否只授权、不播放；
- 第二次交互的业务音效是否真实可闻。

## 验收矩阵

| 场景 | 预期 |
|---|---|
| 首次横滑 | Carousel 正常切换；允许无声；结束后 Context 为 running |
| 第二次横滑 | 播放一次 `change`；只移动一格 |
| 首次纵滑 | 页面正常滚动；允许无声；结束后完成授权 |
| 第二次纵滑 | 对应 `enter`/section 音效正常 |
| Benefits、菜单、FAQ | 沿用既有业务音效 |
| Loader 阶段 | 不污染 Logo、百分比、滚动锁和 3D 登场 |
| 静音状态 | 不绕过用户明确静音 |

## 工程纪律

1. 从人类验收基线建立隔离分支和独立端口。
2. 每轮只改变一个变量，例如事件端点；不要同时更换音频引擎、容器和媒体类型。
3. 修改前先追踪有效路径，区分授权层与播放层。
4. 首次完整交互允许无声，避免强求“第一下就响”。
5. 自动化验证视觉与状态回归，真实设备审批声音。
6. 实机失败立即撤回，不让实验污染稳定基线。
7. 长文件用短区间读写；绝不把工具输出中的 `[truncated]` 写回源码。

## 本项目证据

- 人类验收基线：`ciao-100`，Commit `cfbdd2a`。
- 声音增强分支：`experiment/touchend-unlock`。
- 声音增强 Commit：`ec3f1be`。
- 真实 iPhone 结果：首次横滑或纵滑无声并完成授权，此后全部交互音效正常。
- 实现差异：只把首次音频解锁端点改为 `touchend`；未重建声音引擎，未改变业务音效回调。

## 可复用设计原则

> 不要把浏览器权限做成一项额外任务；把它寄生在用户本来就会完成的首个自然交互上。

这条原则也适用于视频播放、陀螺仪、全屏、剪贴板等能力，但必须分别遵守各 API 对用户激活的具体要求。
