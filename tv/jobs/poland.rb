require_relative 'node_red'

red = NodeRed.new

SCHEDULER.every '10s', first_in: 0 do |job|
  data = red.poland

  send_event('wilgotnosc-gleby', { 
    value: data.dig('wilgotnoscGleby', 1, 'last').round
  })

  data.each do |key, stats|
    start = stats[1]['last'] || 0
    last = stats[0]['last'] || 0

    event = "poland-#{key}"

    send_event(event, {
      current: start, last: last
    })
  end
end
