@echo off
chcp 65001 >nul
echo ========================================
echo 清理项目临时文件和冗余文件
echo FileSearcherV3 Cleanup Script
echo ========================================
echo.

echo [1] 根目录 - 测试/调试脚本:
echo     - check_files.py, check_ppt.py, check_ppt_content.py
echo     - debug_search_index.py
echo     - test_api_response.py, test_frontend_logic.html
echo     - test_indexer_direct.py, test_location_fix.md
echo     - test_ppt_location.py, test_ppt_search.py, test_search.py
echo     - test_index_fix.bat, verify_fix.bat, quick_test.bat
echo.

echo [2] 根目录 - 临时文档:
echo     - ADD_FILE_FEATURE.md, CHANGES_SUMMARY.md
echo     - CURRENT_STATUS_AND_ACTION_PLAN.md, FINAL_TEST_CHECKLIST.md
echo     - FIX_SUMMARY.md, LOCATION_FIX_SUMMARY.md
echo     - UPDATE_PLAN.md, VERIFICATION_CHECKLIST.md
echo.

echo [3] Backend 目录:
echo     - debug_script.py, reindex_test.py
echo     - __pycache__\, build\, dist\ (编译目录)
echo.

echo [4] Frontend 目录:
echo     - src\App.vue.old (旧版本备份)
echo.

echo [5] 根目录临时依赖:
echo     - node_modules\, package.json, package-lock.json (根目录)
echo.

echo ========================================
echo 按任意键继续删除，或关闭窗口取消...
pause >nul

echo.
echo 开始清理...
echo.

REM === 根目录测试/调试脚本 ===
echo 正在删除根目录测试脚本...
del /Q "check_files.py" 2>nul
del /Q "check_ppt.py" 2>nul
del /Q "check_ppt_content.py" 2>nul
del /Q "debug_search_index.py" 2>nul
del /Q "test_api_response.py" 2>nul
del /Q "test_frontend_logic.html" 2>nul
del /Q "test_indexer_direct.py" 2>nul
del /Q "test_location_fix.md" 2>nul
del /Q "test_ppt_location.py" 2>nul
del /Q "test_ppt_search.py" 2>nul
del /Q "test_search.py" 2>nul
del /Q "test_index_fix.bat" 2>nul
del /Q "verify_fix.bat" 2>nul
del /Q "quick_test.bat" 2>nul

REM === 根目录临时文档 ===
echo 正在删除临时文档...
del /Q "ADD_FILE_FEATURE.md" 2>nul
del /Q "CHANGES_SUMMARY.md" 2>nul
del /Q "CURRENT_STATUS_AND_ACTION_PLAN.md" 2>nul
del /Q "FINAL_TEST_CHECKLIST.md" 2>nul
del /Q "FIX_SUMMARY.md" 2>nul
del /Q "LOCATION_FIX_SUMMARY.md" 2>nul
del /Q "UPDATE_PLAN.md" 2>nul
del /Q "VERIFICATION_CHECKLIST.md" 2>nul

REM === 旧版清理列表中的文件（可能仍存在） ===
del /Q "test_fix.py" 2>nul
del /Q "test_enhancements.py" 2>nul
del /Q "test_frontend.py" 2>nul
del /Q "test_ppt_parser.py" 2>nul
del /Q "final_verification.py" 2>nul
del /Q "rebuild_index.py" 2>nul
del /Q "quick_rebuild.py" 2>nul
del /Q "quick_fix_index.bat" 2>nul
del /Q "switch_to_old_ui.bat" 2>nul
del /Q "switch_to_new_ui.bat" 2>nul
del /Q "debug_start.bat" 2>nul
del /Q "stop_dev.bat" 2>nul
del /Q "DIAGNOSIS_PLAN.md" 2>nul
del /Q "ENHANCEMENT_PLAN.md" 2>nul
del /Q "SEARCH_ENHANCEMENT_PLAN.md" 2>nul
del /Q "REDESIGN_PLAN.md" 2>nul
del /Q "UI_COMPARISON.md" 2>nul
del /Q "PROJECT_STATUS_REPORT.md" 2>nul

REM === Backend 目录 ===
echo 正在清理 backend 目录...
del /Q "backend\debug_script.py" 2>nul
del /Q "backend\reindex_test.py" 2>nul
if exist "backend\__pycache__" rmdir /S /Q "backend\__pycache__" 2>nul
if exist "backend\build" rmdir /S /Q "backend\build" 2>nul
if exist "backend\dist" rmdir /S /Q "backend\dist" 2>nul
if exist "backend\app\__pycache__" rmdir /S /Q "backend\app\__pycache__" 2>nul

REM === Frontend 目录 ===
echo 正在清理 frontend 目录...
del /Q "frontend\src\App.vue.old" 2>nul
del /Q "frontend\src\App_New.vue" 2>nul

REM === 根目录临时依赖 (可选，取消注释启用) ===
REM echo 正在清理根目录 node_modules...
REM if exist "node_modules" rmdir /S /Q "node_modules" 2>nul
REM del /Q "package.json" 2>nul
REM del /Q "package-lock.json" 2>nul

echo.
echo ========================================
echo ✅ 清理完成！
echo ========================================
echo.
echo 保留的核心文件:
echo   - README.md, HOW_TO_START.md, QUICK_START.md
echo   - DEPLOYMENT_GUIDE.md, RELEASE_NOTES_V3.1.md
echo   - start_dev.bat, start_backend_only.bat
echo   - cleanup_project.bat (本脚本)
echo   - backend\, frontend\ (核心代码)
echo.
pause
