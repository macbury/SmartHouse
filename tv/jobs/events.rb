require_relative 'node_red'
require 'time'
require 'active_support/all'
require 'action_view'
require 'action_view/helpers'

include ActionView::Helpers::DateHelper

def push_events(events, key)
  all = events.map do |event|
    date = DateTime.parse(event['date'])
    {
      label: event['event'],
      date: date,
      value: distance_of_time_in_words_to_now(date)
    }
  end.sort_by { |e| e[:date]  }

  send_event(key, items: all)
end

SCHEDULER.every '5m', first_in: 0 do |job|
  events = NodeRed.new.events

  push_events(
    (events['personal'] + events['wspolne'] + events['wydatkiArek']),
    'events-arek'
  )

  push_events(events['wydatkiOla'], 'payments-ola')
end