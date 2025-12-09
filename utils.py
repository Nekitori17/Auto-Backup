import os
from datetime import datetime

def variable_replacer(fmt: str, top_folder: str, src_path: str, count: int) -> str:
  """
  Helper function to replace variables in the format string.
  """
  now = datetime.now()
  filename = os.path.basename(src_path)
  name, ext = os.path.splitext(filename)

  res = fmt
  res = res.replace("$date", now.strftime("%Y-%m-%d"))
  res = res.replace("$time", now.strftime("%H-%M-%S"))
  res = res.replace("$timestamp", now.strftime("%Y%m%d_%H%M%S"))
  res = res.replace("$count", str(count + 1)) 
  res = res.replace("$top_folder", top_folder)
  res = res.replace("$filename", filename)
  res = res.replace("$name", name)
  
  return res