# frozen_string_literal: true

require 'yaml'

def pull_vars
  Dir.glob("#{task.application.original_dir}/config/env{,.aws,.rails,.prod}.1p").flat_map do |filename|
    File.readlines(filename).reject { |line| line.start_with? '#' }.map { |line| line.split('=').first }
  end
end

def pull_vars_and_values
  heroku_only = {
    # https://medium.com/klaxit-techblog/tracking-a-ruby-memory-leak-in-2021-9eb56575f731
    'MALLOC_ARENA_MAX' => 2,
    # https://brandonhilkert.com/blog/reducing-sidekiq-memory-usage-with-jemalloc/
    # did not seem to help - https://app.asana.com/0/386347214298196/1205418995354356
    # 'LD_PRELOAD' => '/usr/lib/x86_64-linux-gnu/libjemalloc.so.2',
    'RAILS_ENV' => 'production',
  }
  pull_vars.each_with_object(heroku_only.dup) do |var, h|
    h[var] = ENV.fetch(var)
  end
end

desc 'Populate Heroku config'
task :populate_heroku do
  vars_and_values = pull_vars_and_values

  assignments = vars_and_values.map do |var, value|
    "#{var}=#{value}"
  end
  sh 'heroku', 'config:set', '--app', 'wall-display', *assignments
end
