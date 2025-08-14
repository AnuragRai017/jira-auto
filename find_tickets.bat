@echo off
echo ========================================================================
echo CertifyOS Jira Automation - Find Eligible Tickets
echo ========================================================================
echo.
echo Choose a search option:
echo 1. Find tickets from approved reporters only
echo 2. Find tickets using original JQL query
echo 3. Find tickets using both queries
echo 4. Exit
echo.
set /p option=Select an option (1-4): 

if "%option%"=="1" (
    python find_tickets_multi_query.py --query-type approved-reporters
) else if "%option%"=="2" (
    python find_tickets_multi_query.py --query-type original
) else if "%option%"=="3" (
    python find_tickets_multi_query.py --query-type both
) else if "%option%"=="4" (
    exit
) else (
    echo Invalid option selected.
)

echo.
pause
