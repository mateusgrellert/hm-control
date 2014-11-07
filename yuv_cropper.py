import os
from math import floor

def parseCfg(lines):

	for l in lines:
		toks = l.split()
		if ':' in l:
			idx = toks.index(':')+1
		if 'InputFile' in l:
			path = toks[idx].split('/')[-1]
		if 'SourceWidth' in l:
			w = int(toks[idx])
		elif 'SourceHeight' in l:
			h = int(toks[idx])
	new_w = int(floor(w/64))*64
	new_h = int(floor(h/64))*64

	return [path, w, h, new_w, new_h]

def updateCfg(lines,new_cfg_path):
	new_cfg = open (new_cfg_path,'w')
	
	[inp_path, old_w, old_h, new_w, new_h] = parseCfg(lines)
	yuv_name = inp_path.split('/')[-1]
	yuv_new_name = yuv_name.replace(str(old_w), str(new_w))
	yuv_new_name = yuv_new_name.replace(str(old_h), str(new_h))

	yuv_new_name = 'cropped/'+yuv_new_name
	new_inp_path = 	''.join(inp_path.split('/')[:-1]+[yuv_new_name])
	for l in lines:
		if 'InputFile' in l:
			l = l.replace(inp_path, new_inp_path)
		elif 'SourceWidth' in l:
			l = l.replace(str(old_w),str(new_w))
		elif 'SourceHeight' in l:
			l = l.replace(str(old_h),str(new_h))
		print >> new_cfg, l.strip('\n')

	new_cfg.close()

def cropYuv(lines, dir_path):
	[inp_path, old_w, old_h, new_w, new_h] = parseCfg(lines)

	yuv_name = inp_path.split('/')[-1]

	if os.path.isfile(inp_path):
		yuv = open(inp_path,'r')
	else:
		print 'Video not found: ', yuv_name
		return

	yuv_new_name = yuv_name.replace(str(old_w), str(new_w))
	yuv_new_name = yuv_new_name.replace(str(old_h), str(new_h))
	out_path = 	out_path = ''.join(inp_path.split('/')[:-1]+[yuv_new_name])
	
	if os.path.isfile(dir_path+out_path): # if cropped yuv already exists, skip it
		return

	new_yuv = open(dir_path+out_path,'w')

	w_offset = (old_w - new_w)
	h_offset = (old_h - new_h) * old_w

	buff = 1
	while(buff):
		# luma layer
		for i in range(0,new_h):
			buff = yuv.read(new_w)
			new_yuv.write(buff)
			yuv.seek(w_offset,1)	# skip remaining cols

		yuv.seek(h_offset,1)  # skip remaining rows

		# chroma layers -- cosidering a 4:2:0 subsampling
		acum = 0
		for chroma in range(0,2):
			for i in range(0,new_h >> 1):
				buff = yuv.read(new_w >> 1)
				acum += (new_w >> 1)
				new_yuv.write(buff)
				yuv.seek(w_offset >> 1,1)
							
			acum += (h_offset>> 2)
			yuv.seek(h_offset>> 2,1) 

		acum = 0
	yuv.close()
	new_yuv.close()

cfgs = os.listdir('/home/grellert/hm-cfgs/')
cfg_path = '/home/grellert/hm-cfgs/cropped/'
dir_path = '/home/grellert/origCfP/cropped/'


for cfg in cfgs:
	if '.cfg' in cfg:
		f = open('/home/grellert/hm-cfgs/'+cfg,'r')
		lines = f.readlines()
		f.close()
		cropYuv(lines, dir_path)
		new_cfg_path = cfg_path+cfg
		updateCfg(lines, new_cfg_path)
	
	
