# while true
# do
# python INDEX.py
# sleep 1
# done

# until ./INDEX.py; do
#     echo "'INDEX.py' crashed with exit code $?. Restarting..." >&2
#     sleep 1
# done



# :main_loop
# python INDEX.py
# echo "Python process finished. Press Ctrl+C now to quit."
# for /l %%i in (5,-1,1) do (
#     echo Restarting in %%i
#     choice /t 1 /d y > nul
# )
# echo "Starting..."
# goto :main_loop