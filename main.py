import time, socketio, base64, requests


class BitSet:
	def __init__(self, base64_string, count=0):
		self.bytes = bytearray(base64_string)
		self.check_count = count

	def get(self, index):
		byte_index = index // 8
		bit_offset = 7 - (index % 8)
		return (self.bytes[byte_index] & (1 << bit_offset)) != 0

	def set(self, index, value):
		if isinstance(value, bool):
			value = 1 if value else 0
		byte_index = index // 8
		bit_offset = 7 - (index % 8)
		current = self.bytes[byte_index] & (1 << bit_offset)
		if value:
			self.bytes[byte_index] |= 1 << bit_offset
			if current == 0:
				self.check_count += 1
		else:
			self.bytes[byte_index] &= ~(1 << bit_offset)
			if current != 0:
				self.check_count -= 1


sio = socketio.Client()
fart = sio.connect('https://onemillioncheckboxes.com/', transports='websocket')

headers = {
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Referer': 'https://onemillioncheckboxes.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

response = requests.get('https://onemillioncheckboxes.com/api/initial-state', headers=headers)
state = BitSet(base64.b64decode(response.json()['full_state']))


while True:
	start = time.perf_counter()
	for i in range(1, 1000000):
		if state.get(i):
			continue
		try:
			sio.emit(event="toggle_bit", data={"index": i})
		except Exception as e:
			print(i)

		time.sleep(0.01)

	print(time.perf_counter() - start)
