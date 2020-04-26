require_relative 'node_red'

red = NodeRed.new

SCHEDULER.every '10m', first_in: 0 do |job|
  data = red.poland

  send_event('wilgotnosc-gleby', { 
    value: data.dig('wilgotnoscGleby', 1, 'last').round
  })

  data.each do |key, stats|
    start = stats[1]['last']&.round(2)
    last = stats[0]['last']&.round(2)

    event = "poland-#{key}"

    send_event(event, {
      current: start, last: last
    })
  end
end