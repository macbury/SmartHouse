require_relative 'node_red'

currency = [
  'usdToPln',
  'gpbToPln',
  'eurToPln',
  'chfToPln'
]

crypt = [
  'ethToPln',
  'btcToPln',
  'oil',
]

resources = [
  'goldToPln',
  'e95ToPln'
]

def emit_ranges_for(group, data, range)
  group.each do |currency|
    valuations = data[currency]
    start = valuations[2]['last']&.round(2)
    last = valuations[1]['last']&.round(2)

    send_event("currency-#{currency}", {
      current: start, last: last
    })
  end
end

red = NodeRed.new

SCHEDULER.every '30s', first_in: 0 do |job|
  data = red.currencies

  emit_ranges_for(currency, data, -20)
  emit_ranges_for(crypt, data, -5)
  emit_ranges_for(resources, data, -200)
end