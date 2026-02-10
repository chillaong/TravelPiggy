# 旅行小猪 (Travel Piggy)

一个基于HTML5/CSS3/JavaScript的休闲网页游戏，玩家可以喂养小猪，让它去世界各地旅行并带回明信片。

## 项目简介

这是一个温馨的养成类小游戏，玩家通过收集星星购买物品，给小猪出发旅行，归来时会带回各地的风景明信片。

## 游戏特色

- 🏠 **房间场景**：小猪在家休息，可以与它互动
- 🌟 **花园场景**：星星会自动生成，点击收集星星
- 🎒 **商店/背包系统**：用星星购买物品，放入背包后选择出发
- ✈️ **旅行系统**：选择任意物品即可出发，归来带回明信片
- 📷 **相册系统**：收集小猪带回的旅行明信片
- 💾 **自动保存**：星星数量和相册内容自动保存到本地存储

## 项目结构

```
小猪页游素材/
├── index.html              # 主游戏文件（已重命名）
├── assets/                 # 资源文件夹
│   ├── scenes/             # 场景图片
│   │   ├── room.png        # 房间背景
│   │   ├── magic_garden.png# 魔法花园
│   │   └── postcards/      # 明信片图片（A 视角）
│   ├── postcards_by_drone/ # 明信片图片（无人机 B 视角）
│   ├── characters/         # 角色图片
│   │   ├── pig_idel.png
│   │   ├── pig_back.png
│   │   ├── pig_travel.png
│   │   └── pig_selfie.png
│   ├── items/              # 物品图片（已拆分为单图，兼容原图集）
│   │   ├── items.png       # （兼容旧引用）
│   │   ├── star.png
│   │   ├── chocolate.png
│   │   ├── granola_bar.png
│   │   ├── burger.png
│   │   ├── bento.png
│   │   ├── tent.png
│   │   ├── camera.png
│   │   └── drone.png
│   ├── ui/                 # UI元素
│   │   ├── frame.png
│   │   ├── WorldMap_UI.jpg
│   │   ├── diary.png
│   │   ├── stars.png
│   │   └── stores.png
│   └── config/             # 运行时可编辑的 CSV 配置
│       ├── locations.csv   # 地点数据 (id,name,x,y,tier,img,img_B,text1,text2,text3)
│       ├── items.csv       # 道具数据 (name,cost,time,img)
│       ├── game_config.csv # 常量配置 (key,value)
│       └── ui_text.csv     # UI 文案配置 (key,text)
├── .gitignore              # Git忽略文件
├── README.md               # 项目说明文档
└── .github/workflows/      # GitHub Actions配置
  └── deploy.yml          # 自动部署配置
```

## 如何运行

### 方法一：使用Python HTTP服务器（推荐）

```bash
# 进入项目目录
cd /Users/avaswork/Desktop/小猪页游素材

# 启动HTTP服务器
python3 -m http.server 8000

# 在浏览器中打开
# http://localhost:8000/
```

### 方法二：直接打开

直接在浏览器中打开 `index.html` 文件即可。

注意：游戏现在从 `assets/config/` 下的 CSV 文件动态加载地点、道具、UI 文案和常量配置，编辑这些 CSV 即可调整游戏数据（无需改代码）。CSV 文件请以 UTF-8 编码保存。

## 游戏玩法

1. **收集星星**：切换到花园场景，星星会按配置节奏生成，点击星星收集
2. **购买物品**：点击商店图标打开商店，用星星购买物品
3. **背包装备**：打开背包，选择任意物品出发
4. **等待归来**：小猪旅行时间结束后会自动归来，带回一张明信片
5. **查看相册**：点击右上角相册图标查看收集的明信片

## 物品列表

| 物品名称 | 星星消耗 | 旅行时间 |
| -------- | -------- | -------- |
| 巧克力   | 5 ⭐     | 0.5 分钟 |
| 汉堡     | 20 ⭐    | 3 分钟   |
| 帐篷     | 30 ⭐    | 5 分钟   |
| 能量棒   | 8 ⭐     | 1 分钟   |
| 便当     | 20 ⭐    | 3 分钟   |
| 相机     | 50 ⭐    | 8 分钟   |
| 无人机   | 80 ⭐    | 10 分钟  |

## 技术栈

- HTML5
- CSS3 (动画、响应式设计)
- JavaScript (ES6+)
- LocalStorage (数据持久化)
- GitHub Actions (自动部署)

## 浏览器兼容性

- Chrome (推荐)
- Firefox
- Safari
- Edge

## 开发说明

游戏采用9:16竖屏设计，适配移动端和桌面端。所有数据使用LocalStorage存储，无需后端服务器。

## 许可证

本项目仅供学习和娱乐使用。

## 更新日志

- v1.4.0 - 2026-02-10
  - 新增旅行目的地：意大利、日本、瑞士，支持A/B视角明信片素材
  - 新增道具：椰子，支持权重加成
  - 实现目的地冷却机制，防止重复旅行
  - 优化权重分配逻辑，支持动态调整
  - 更新配置表结构，支持更灵活的游戏内容调整

- v1.3.0 - 2026-02-09
  - 新增 UI 文案配置表（assets/config/ui_text.csv），所有 UI 文案可配置
  - 新增初始星星与产出速率配置（initial_stars / stars_per_second）
  - 明信片 A/B 视角资源路径调整
  - 背包选择任意物品即可出发旅行

- v1.2.0 - 2026-02-09
  - 将地点、道具和游戏常量抽取为 CSV 配置（assets/config/），支持运行时编辑
  - 将 items 图集拆分为单独图标（assets/items/*），并将页面改为按单图加载
  - 更新商店道具：新增能量棒、便当、相机、无人机（并在 `assets/config/items.csv` 中配置）
  - 改为异步加载配置并在初始化时读取 CSV，移除部分硬编码常量

- v1.1.0 - 2026-02-08
  - 优化项目结构，分类整理图片资源
  - 重命名主文件为index.html
  - 增大星星元素大小，优化视觉效果
  - 更新商店物品时间设置：巧克力(0.5分钟)、汉堡(3分钟)、帐篷(5分钟)
  - 改进相片模态框关闭逻辑，添加专门的关闭按钮
  - 优化星星收集动画，使飞星特效准确指向星星数量显示区域
  - 部署到GitHub Pages，配置自动部署 workflow

- v1.0.0 - 初始版本发布
  - 基础游戏功能
  - 房间和花园场景
  - 商店和旅行系统
  - 相册系统
  - 本地数据保存
