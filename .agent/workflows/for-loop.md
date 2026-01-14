---
description: 啟動自動修復迴圈 - AI 必須持續執行直到腳本判定完成
---

# For Loop - 自動修復迴圈

這個 Workflow 啟動一個由**腳本控制**的自動修復迴圈。

**重要**：你的停止權限由 `check-completion.sh` 腳本控制，不是你自己決定。

---

## 啟動流程

// turbo
### 步驟 1：初始化

執行以下命令初始化迴圈狀態：

```bash
bash ./commands/for-loop.sh "$TASK_DESCRIPTION" --max-iterations $MAX_ITERATIONS --test-command "$TEST_COMMAND"
```

參數說明：
- `$TASK_DESCRIPTION`: 任務描述（例如：「修復所有 TypeScript 錯誤」）
- `$MAX_ITERATIONS`: 最大迭代次數（預設 10）
- `$TEST_COMMAND`: 測試命令（預設 `npm test`）

---

## 迴圈執行

// turbo-all
### 步驟 2：執行任務

根據任務描述和錯誤訊息，修改代碼。

### 步驟 3：強制檢查點

**每次修改代碼後，必須執行：**

```bash
bash ./commands/check-completion.sh
```

### 步驟 4：解讀腳本輸出並執行

腳本會輸出以下其中一種結果，**你必須遵守**：

| 腳本輸出 | 你的行動 |
|---------|---------|
| `DONE` | 任務完成，可以停止 |
| `CONTINUE: <訊息>` | **禁止停止**，必須根據訊息繼續修復，回到步驟 2 |
| `STUCK: <訊息>` | 陷入死循環，停止並報告問題 |
| `ERROR: <訊息>` | 發生錯誤，嘗試解決或報告 |

### 步驟 5：迴圈

如果步驟 4 的結果是 `CONTINUE`，**必須**回到步驟 2 繼續修復。

**禁止**在收到 `CONTINUE` 時停止工作。

---

## 強制規則

1. **腳本說了算**：`check-completion.sh` 的輸出是唯一的判斷標準
2. **禁止自作主張**：不能因為「我覺得改好了」就停止
3. **禁止跳過檢查**：每次修改後必須執行 `check-completion.sh`
4. **必須報告進度**：每次迭代開始時報告「迭代 N/M」

---

## 取消迴圈

如果用戶要求取消，執行：

```bash
bash ./commands/cancel-loop.sh
```

---

## 範例流程

```
用戶: /for-loop "修復所有 ESLint 錯誤" --max-iterations 5

AI: 開始迭代 1/5...
    [修改代碼]
    執行 check-completion.sh

腳本: CONTINUE: 測試失敗 (迭代 1/5)
      # 錯誤: 3 ESLint errors found

AI: 繼續修復，迭代 2/5...
    [修改代碼]
    執行 check-completion.sh

腳本: CONTINUE: 測試失敗 (迭代 2/5)
      # 錯誤: 1 ESLint error found

AI: 繼續修復，迭代 3/5...
    [修改代碼]
    執行 check-completion.sh

腳本: DONE
      # 所有測試通過！

AI: 任務完成！共迭代 3 次。
```
