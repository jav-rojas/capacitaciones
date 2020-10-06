import random

class to_HTML():
  
  # Attributes
  default_text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
  
  default_video = ["https://www.youtube.com/embed/JGXi_9A__Vc","https://www.youtube.com/embed/UjtOGPJ0URM","https://www.youtube.com/embed/3g246c6Bv58"]
  
  def __init__(self):
    self.random = random.randint(0,2)

  # Internal methods
  def nth_replace(self, s, sub, repl, n):
      find = s.find(sub)
      i = find != -1
      while find != -1 and i != n:
          find = s.find(sub, find + 1)
          i += 1
      if i == n:
          return s[:find] + repl + s[find+len(sub):]
      return s    

  # Methods
  def paragraph(self, text = default_text, links = None, new_tab = False):
      # Guarda el texto
      self.text = text
      # ¿En nueva pestaña?
      self.new_tab = ""
      if new_tab:
        self.new_tab = "target = _blank"
      self.anchors = []
      # Si hay links, intentará reemplazar los tags correspondientes
      if links:  
        # Itera sobre links
        for i in range(0,len(links)):
          if links[i]:
            if links[i][1]:
              self.anchors.append("<a href = '{}' {} rel='noopener noreferrer'>{}</a>".format(links[i][0],self.new_tab,links[i][1]))
          else:
            anchor.append("Error al reemplazar")
      
      if self.anchors:
        for i in range(0,len(self.anchors)):
          self.text = self.nth_replace(self.text, "___", self.anchors[i], 1)
      self.HTML = "<p style = 'font-size:14px;'>"+self.text+"</p>"
      return self.HTML
  
  def video(self, link = False):
    if not link:
      self.random_default = self.default_video[self.random]
      self.link = '<iframe id="ytplayer" type="text/html" width="698" height="405" src="{}" frameborder="0" allowfullscreen>'.format(self.random_default)
    else:
      self.link = '<iframe id="ytplayer" type="text/html" width="698" height="405" src="{}" frameborder="0" allowfullscreen>'.format(link)
    return self.link