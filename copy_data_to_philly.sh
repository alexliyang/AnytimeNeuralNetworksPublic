
export PHILLY_VC=msrlabs

local_folder=/home/dedey/DATADRIVE1/ann_data_dir
#remote_folder_gcr=hdfs://gcr/msrlabs/dedey/ann_data_dir/
#remote_folder_cam=hdfs://cam/msrlabs/dedey/ann_data_dir/
remote_folder_rr1=hdfs://rr1/msrlabs/dedey/

# Copy to rr1
echo "Copying data to rr1"
python /home/dedey/Dropbox/philly/philly_tool/tool_04_19_17_python_2.7/philly-fs.pyc -cp -r $local_folder $remote_folder_rr1
echo "Finished copying data to rr1"


# Copy to gcr
#echo "Copying data to gcr"
#python /home/dedey/Dropbox/philly/philly_tool/tool_04_19_17_python_2.7/philly-fs.pyc -cp -r $local_folder $remote_folder_gcr
#echo "Finished copying data to gcr"

# Copy to cam
#echo "Copying data to cam"
#python /home/dedey/Dropbox/philly/philly_tool/tool_04_19_17_python_2.7/philly-fs.pyc -cp -r $local_folder $remote_folder_cam
#echo "Finished copying data to cam"
