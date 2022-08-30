@echo off

call conda activate o3

set CMD=%1

IF [%1]==[] goto USAGE

IF %CMD%==view goto VIEW
IF %CMD%==space goto SPACE 
IF %CMD%==cycle goto CYCLE

IF %CMD%==merge goto MAKE_MERGE
IF %CMD%==mask goto MAKE_MASK
IF %CMD%==normal goto MAKE_NORMAL
IF %CMD%==poify goto DEPTH_TO_POINTS
IF %CMD%==unpack goto UNPACK_VIDEO

IF %CMD%==co goto CTX 
IF %CMD%==layer goto LAYER 
IF %CMD%==cam goto CAM





:USAGE
echo ---------------------------------------------------------------------------
echo -                              p3 p3 p3                                   -
echo -                              p3      p3    333333                       -
echo -                              p3      p3   3    333                      -
echo -                              p3 p3 p3        3333                       -
echo -                              p3           3    333                      -
echo -                              p3            333333                       -
echo ---------------------------------------------------------------------------
echo "space & percpection:
echo ---------------------------------------------------------------------------
echo "p3 view <png mesh pattrn>  : render depth frame, and meshes(exclude pattern)"
echo "p3 cycle <glob destpath>   : cycle image(s) from source, i.e. p3 cycle *.png test.png"
echo "p3 space <>                : space testing
echo ---------------------------------------------------------------------------
echo "depth & mesh"
echo ---------------------------------------------------------------------------
echo "p3 poify <png>             : generate point cloud from depth frame"
echo "p3 mask <obj>              : make mask file from source object file
echo "p3 merge <obj obj outpath> : merge two obj mesh files into one output file
echo "p3 normal <obj>            : make mask file from source object file
echo "p3 unpack <mp4>            : extract frames from mp4 video
echo ---------------------------------------------------------------------------
echo "p3 layer <png>             : draw/animate an image that is being continously overwritten"
echo "p3 anim <depth obj>        : live depth fram with mesh, i.e p3 cam file.obj"
echo "p3 capture                 : capture snapshot of renderer frame"
echo ---------------------------------------------------------------------------
echo "engine graph & context"
echo ---------------------------------------------------------------------------
echo "p3 co <name>               : print or change p3 origin in engine graph context "
echo "p3 add <node>              : add zone, obj, input, to graph"
goto END

:MAKE_MERGE
python "%PC3_ROOT%/tools/src/merge_meshes.py" %2 %3 %4
goto END


:MAKE_MASK
python "%PC3_ROOT%/tools/remake_mask.py" %2
goto END

:MAKE_NORMAL
python "%PC3_ROOT%/tools/remake_normals.py" %2
goto END

:DEPTH_TO_POINTS
python %PC3_ROOT%/tools/src/d2p.py %2
goto END

:UNPACK_VIDEO/
python %PC3_ROOT%/tools/src/p3_vid2png.py %2
goto END


:CAM
pc3 *.png %2
goto END

:INIT
mkdir "c:/tmp/p3/%2"
goto END

:CD_CFG
set P3_WS=/tmp/p3/%2
cd %P3_WS%
echo %P3_WS%
echo 
goto END

:CTX
git config user.email
echo PC3_ROOT     : %PC3_ROOT%
echo P3_WORKSPACE : %P3_WS%
echo P3_MESHFILE  : %P3_MESHFILE%
goto END

:VIEW
rem pc3 %2 %3 
set PC3_FILEPATH=%2
set P3_MESHPATH=%3
set P3_MASKPATTERN=%4
python %PC3_ROOT%/tools/pc3_app.py --samples 0 -vs yes
goto END

:SPACE
python %PC3_ROOT%/tools/space_editor.py %2  %3 %4 %5  %6 %7 %8
goto END

:LAYER
echo %2 %3 %4
p3loop.cmd %2 /tmp/config/default.json %INSTALL% %3
goto END

:CYCLE
python "%PC3_ROOT%/tools/src/imgcycle.py" %2 %3
goto END

:END


