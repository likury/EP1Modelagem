#!/bin/sh
img_dir=../img/
data_dir=../data
cmd=./gera_graficos.py

for file in $data_dir/rodovia*.json; do
  $cmd $file $img_dir
done

exit 0
