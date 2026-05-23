# 钢铁表面缺陷检测系统 (Steel Defect Detection)

基于 YOLOv11 的工业表面缺陷检测 Web 应用。支持检测 6 类钢材表面缺陷：**裂纹(crazing)、划痕(inclusion)、斑块(patches)、麻点(pitted_surface)、压入(rolled-in_scale)、氧化皮(scratches)**。

## 📋 目录

- 项目简介
- 技术栈
- 团队协作指南（Git/GitHub）
	- 一、组长初始化操作
	- 二、组员第一次加入
	- 三、每日开发流程（组员必读）
	- 四、组长审核 Pull Request
- 环境搭建
	- 后端环境（Python）
	- 前端环境（Node.js）
	- 数据库与存储（Docker）
- 数据集准备与模型训练
	- 下载 NEU-DET 数据集
	- 转换为 YOLO 格式
	- 训练模型
- 运行项目
	- 启动后端服务
	- 启动前端服务
- 常见问题

------

## 项目简介

本项目是一个完整的工业缺陷检测系统，采用前后端分离架构：

- **后端**：FastAPI + YOLOv11 + PostgreSQL + Redis + MinIO
- **前端**：Vue3 + Element Plus + Axios
- **部署**：Docker Compose

用户上传钢材表面图片，系统实时返回缺陷类型、置信度和位置框，并保存检测历史。

------

## 技术栈

| 层       | 技术                  |
| :------- | :-------------------- |
| 目标检测 | YOLOv11 (Ultralytics) |
| 后端框架 | FastAPI               |
| 前端框架 | Vue3 + Vite           |
| UI组件   | Element Plus          |
| 数据库   | PostgreSQL            |
| 缓存     | Redis                 |
| 对象存储 | MinIO                 |
| 容器化   | Docker Compose        |

------

## 团队协作指南（Git/GitHub）

本指南面向零基础成员，**请所有人仔细阅读并严格遵循**。

### 一、组长初始化操作（只做一次）

1. **创建 GitHub 仓库**（已完成）

2. **添加组员为协作者**

	- 仓库页面 → Settings → Collaborators → Add people → 输入组员 GitHub 账号 → 权限 Write

3. **设置分支保护**

	- Settings → Branches → Add rule → `develop` → 勾选 “Require a pull request before merging” → 勾选 “Require approvals (1)” → Create
	- 同样为 `main` 添加相同规则

4. **本地初始化并推送**

	bash

	```
	git clone git@github.com:DreamboatJY/steel-defect-detection.git
	cd steel-defect-detection
	git checkout -b develop
	git push -u origin develop
	```

	

### 二、组员第一次加入

1. **安装 Git**（[下载地址](https://git-scm.com/downloads)），配置用户名和邮箱：

	bash

	```
	git config --global user.name "你的名字"
	git config --global user.email "你的邮箱"
	```

	

2. **生成 SSH 密钥并添加到 GitHub**（免密登录）：

	bash

	```
	ssh-keygen -t rsa -b 4096 -C "你的邮箱"   # 一路回车
	cat ~/.ssh/id_rsa.pub                     # 复制输出
	```

	

	登录 GitHub → Settings → SSH and GPG keys → New SSH key → 粘贴 → Add SSH key
	测试：`ssh -T git@github.com` 应显示 `Hi 用户名!...`

3. **克隆仓库**：

	bash

	```
	git clone git@github.com:DreamboatJY/steel-defect-detection.git
	cd steel-defect-detection
	git checkout develop
	```

	

### 三、每日开发流程（组员必读）

**核心原则**：永远不在 `develop` 或 `main` 上直接修改。所有改动都通过「功能分支 → Pull Request → 合并」完成。

#### 每天开始工作（上午 9:00）

bash

```
# 1. 切换到 develop 并拉取最新代码（同步队友的更新）
git checkout develop
git pull

# 2. 创建自己的功能分支（分支名格式：类型/任务-姓名）
#    类型：feature（新功能）、bugfix（修复）、docs（文档）
git checkout -b feature/添加检测历史-张三
```



#### 开发过程中（随时）

bash

```
# 查看当前修改了哪些文件
git status

# 添加修改的文件
git add .                 # 添加所有
# 或指定文件：git add backend/app/services/detection_service.py

# 提交到本地仓库（-m 后面写简短描述）
git commit -m "feat: 实现历史记录接口"

# 推送到远程（备份，防止丢失）
git push origin feature/添加检测历史-张三
```



#### 任务完成后（下午 17:00 前）

1. **在 GitHub 网页上发起 Pull Request (PR)**

	- 打开仓库 → Pull requests → New pull request
	- `base` 选择 `develop`，`compare` 选择你的分支（如 `feature/添加检测历史-张三`）
	- 填写标题和描述 → Create pull request
	- 右侧 Reviewers 选择组长

2. **等待组长审核**（组长会批准或要求修改）

3. **PR 合并后**，本地的功能分支可以删除（可选）：

	bash

	```
	git checkout develop
	git pull
	git branch -d feature/添加检测历史-张三
	```

	

### 四、组长审核 Pull Request

1. 收到 GitHub 通知（邮件或网页铃铛图标）
2. 进入仓库 → Pull requests → 点击待审核的 PR
3. 点击 `Files changed` 查看代码改动
4. 如果没问题，点击 `Review changes` → 选择 `Approve` → `Submit review`
5. 点击 `Merge pull request` → `Confirm merge`
6. （可选）勾选 “Delete branch” 删除远程分支

> 如果出现冲突（Conflicts），可以要求组员在本地解决后重新推送，或组长在网页上点击 `Resolve conflicts` 手动编辑。

------

## 环境搭建

### 后端环境（Python）

组长使用 conda 环境 `你的conda环境名`（已安装 torch 和 ultralytics），组员使用虚拟环境 `.venv`。

#### 组长（使用已有 conda 环境）

bash

```
conda activate 组长的conda环境名
pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```



#### 组员（使用项目虚拟环境）

bash

```
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```



### 前端环境（Node.js）

bash

```
cd frontend
npm install
```



### 数据库与存储（Docker）

bash

```
docker-compose up -d   # 启动 PostgreSQL, Redis, MinIO
docker-compose ps      # 查看状态
```



------

## 数据集准备与模型训练

### 下载 NEU-DET 数据集

从官方下载（发布者主页）

解压到 `datasets/NEU-DET/`，目录结构应为：

text

```
datasets/NEU-DET/
    IMAGES/      # 所有 .jpg 图片
    ANNOTATIONS/ # 所有 .xml 标注文件
```



### 转换为 YOLO 格式

运行脚本 `convert.py`（组长本地，未上传仓库）：

bash

```
conda activate PyTorchDL
python convert.py
```



输出目录：`datasets/neu_det_yolo/`（包含 `images/train`, `images/val`, `labels/train`, `labels/val` 和 `data.yaml`）

### 训练模型

bash

```
python train.py
```



训练参数已在 `train.py`（组长本地，未上传仓库）中配置（100 轮，batch=16，混合精度）。完成后最佳模型保存在 `neu_detector/exp/weights/best.pt`。
训练支持断点续训：如果中途中断，再次运行 `python train.py` 会自动从上次中断处继续。

------

## 运行项目

### 启动后端服务

bash

```
cd backend
# 激活环境（conda 或 .venv）
conda activate 你的conda环境名    # 或 .venv\Scripts\activate
python main.py
```



访问 API 文档：http://localhost:8000/docs

### 启动前端服务

bash

```
cd frontend
npm run dev
```



访问：[http://localhost:5173](http://localhost:5173/)

------

## 常见问题

| 问题                 | 解决方法                                                     |
| :------------------- | :----------------------------------------------------------- |
| git push 被拒绝      | 先 `git pull` 再 `git push`                                  |
| 忘记创建分支就开发了 | `git checkout -b 新分支名`（当前修改会保留）                 |
| 合并时发生冲突       | 打开冲突文件，删除 `<<<<<<<`, `=======`, `>>>>>>>`，保留正确代码，然后 `git add . && git commit` |
| pip 安装慢           | 使用清华源：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple` |
| Docker 端口被占用    | 修改 `docker-compose.yml` 中的端口映射                       |
| 训练时显存不足       | 降低 `train.py` 中的 `batch` 值（如 16 → 8 或 4）            |

------

## 项目结构

text

```
steel-defect-detection/
├── backend/                # FastAPI 后端
│   ├── app/                # 应用代码
│   ├── static/             # 上传/结果图片（不提交）
│   ├── .venv/              # Python 虚拟环境（不提交）
│   ├── requirements.txt
│   └── main.py
├── frontend/               # Vue3 前端
│   ├── src/
│   ├── node_modules/       # 不提交
│   └── package.json
├── datasets/               # 数据集（不提交）
├── storage/                # Docker 数据（不提交）
├── docker-compose.yml
├── .gitignore
└── README.md
```



------

## 联系方式

组长：DreamboatJY
仓库地址：https://github.com/DreamboatJY/steel-defect-detection

祝项目顺利！ 🚀