import random

class to_HTML():
  
  default_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
  
  default_video = ["https://www.youtube.com/embed/JGXi_9A__Vc","https://www.youtube.com/embed/UjtOGPJ0URM","https://www.youtube.com/embed/3g246c6Bv58"]
  
  def __init__(self):
    self.random = random.randint(0,2)
    
  def paragraph(self,text = default_text):
    self.HTML = "<p style = 'font-size:14px;'>"+text+"</p>"
    return self.HTML
  
  def video(self, link = False):
    if not link:
      self.random_default = self.default_video[self.random]
      self.link = '<iframe id="ytplayer" type="text/html" width="698" height="405" src="{}" frameborder="0" allowfullscreen>'.format(self.random_default)
    else:
      self.link = '<iframe id="ytplayer" type="text/html" width="698" height="405" src="{}" frameborder="0" allowfullscreen>'.format(link)
    return self.link