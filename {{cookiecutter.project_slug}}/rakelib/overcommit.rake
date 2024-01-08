# frozen_string_literal: true

desc 'Run overcommit on current code'
task overcommit: :environment do
  sh 'overcommit --run'
end
