# 上传 GitHub 操作手册（本文件不用提交到仓库，看完可删）

## 0) 仓库名（三选一，本包目录已按推荐名命名）
- **`lung-tumor-2d-unet`（推荐）**：搜索友好、见名知义
- `LungSeg-2D`：更短的"品牌名"
- `msd-task06-2d-unet`：数据集导向

在 github.com 网页上 New repository 时用同名（选 Public、**不要**勾选自动生成 README/.gitignore/License——本包已带）。

## 1) 把本包解压覆盖到你的项目目录
解压 `lung-tumor-2d-unet.zip`，将内容合并进 `D:\pythonprojects\practice-github\UNET\`
（或把 UNET 目录里除 data/ 外的旧文件清掉后整体替换——代码以本包为准）。
注意：`data/` 整个目录已被 .gitignore 排除，不会被上传。

## 2) 补两张你机器上的素材（README 已引用以下路径）
三联图示例（挑 3~6 张有肿瘤且分割效果好的）：
```powershell
New-Item -ItemType Directory -Force docs\figures\samples
Copy-Item data\preds_v4\*.png docs\figures\samples\
# 然后从 samples 里挑几块重命名为 sample_1.png ~ sample_4.png，删掉其余
```
README 里的示例图区块已按 `docs/figures/samples/sample_1.png` ~ `sample_4.png` 写好，
复制完即显示（详见下）。

曲线图和 Dice 分布图我已经用你的真实 train_log/CSV 生成好了，无需重做；
v5 训练跑完后想更新：
```powershell
python make_figures.py --log data\checkpoints\train_log.txt --csv data\preds_v4\dice_per_slice.csv --out docs\figures
```

## 3) 取消 README 中示例图区块的注释
打开 README.md，找到 `<!-- SAMPLES ... -->` 注释块，删掉两行注释标记。
（GitHub 不会渲染失效图片链接，所以默认注释着，复制完图片再放开。）

## 4) LICENSE 填名字
把 LICENSE 第 3 行 `<Your Name>` 改成你的名字/GitHub ID。

## 5) 推送（6 条命令）
```powershell
cd D:\pythonprojects\practice-github\UNET
git init
git add .
git commit -m "Initial release: 2D U-Net lung tumor segmentation (MSD Task06)"
git branch -M main
git remote add origin https://github.com/<你的用户名>/lung-tumor-2d-unet.git
git push -u origin main
```
首次 push 会弹浏览器登录 GitHub 授权。

## 6) 推完自检
- 打开仓库网页：README 渲染、两张 docs/figures 图、示例图都显示；
- 确认仓库里**没有** data/、*.pth、*.nii.gz（.gitignore 应已拦住，网页上看一眼最稳）；
- About 栏填一句描述 + topics：`pytorch` `unet` `medical-imaging` `segmentation` `msd`。

## 7) v5 结果出来后
更新 README 结果表（两行数字）+ 重跑 make_figures.py + 重新 commit/push 即可。
