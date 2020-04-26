require 'httparty'

class NodeRed
  include HTTParty
  base_uri ENV.fetch('NODE_RED')

  def unread
    self.class.get('/data/unread')
  end

  def events
    self.class.get('/data/events')
  end

  def currencies
    self.class.get('/data/currencies')
  end

  def poland
    self.class.get('/data/poland')
  end

  def grocy
    self.class.get('/data/grocy')
  end
end