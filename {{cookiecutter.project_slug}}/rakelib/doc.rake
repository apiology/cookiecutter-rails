# frozen_string_literal: true

desc 'Push documentation updates to Dropbox'
task doc: :environment do
  sh 'yard -p yard_templates -o docs/ --no-private'
end
