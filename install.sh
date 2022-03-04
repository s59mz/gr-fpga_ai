# Install the project...

mkdir -p /usr/lib/cmake/fpga_ai/
cp ../gr-fpga_ai/cmake/Modules/fpga_aiConfig.cmake /usr/lib/cmake/fpga_ai/

mkdir /usr/include/fpga_ai/
cp ../gr-fpga_ai/include/fpga_ai/api.h /usr/include/fpga_ai/

mkdir /usr/lib/python3/dist-packages/fpga_ai/
cp ../gr-fpga_ai/python/*.py /usr/lib/python3/dist-packages/fpga_ai/

cp ../gr-fpga_ai/grc/*.yml /usr/share/gnuradio/grc/blocks/

