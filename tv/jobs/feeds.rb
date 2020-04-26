require_relative 'node_red'

SCHEDULER.every '10s', first_in: 0 do |job|
  entries = NodeRed.new.unread.map do |entry|
    { name: entry.dig('feed', 'title'), body: entry.dig('title'), avatar: '' }
  end

  send_event('feeds', comments: entries)
end