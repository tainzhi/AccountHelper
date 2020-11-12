import cpca

# 是否对selenium截的全屏图裁剪, 默认截全屏图
IS_CROP_IMAGE = False


class Util:
	@staticmethod
	def is_same_address(address1, address2):
		"""
		地址转换后, 格式类似这样的, 省/市/区/地址/邮编, 不存在则为None
		['福建省' '泉州市' None '洛江万安塘西工业区安邦路10号' '350500']
		['福建省' '泉州市' '洛江区' '万安塘西工业区安邦路9号' '350504']
		"""
		data = cpca.transform([address1.strip(), address2.strip()]).values
		# 地址1
		a1 = data[0]
		# 地址2
		a2 = data[1]
		# 省
		if a1[0] != a2[0]:
			return False
		# 市
		if a1[1] != a2[1]:
			return False
		# 区
		if a1[2] != a2[2]:
			return False
		# 比较详细地址
		if len(a1[3]) != len(a2[3]):
			return False
		for x, y in zip(a1[3], a2[3]):
			if x != y:
				return False
		return True

	@staticmethod
	def split_list_average_n(origin_list, n):
		"""
		list均分成 n 份
		"""
		# +1是取float 上限 ceil， 不+1会产生 n+1个数组
		each_count = int(len(origin_list) / n) + 1
		for i in range(0, len(origin_list), each_count):
			yield origin_list[i: i + each_count]
