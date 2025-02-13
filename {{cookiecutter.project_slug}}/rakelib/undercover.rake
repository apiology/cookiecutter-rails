# frozen_string_literal: true

desc 'Ensure PR changes are fully covered by tests'
task undercover: :environment do |_t|
  ret =
    system("if git branch -r | grep origin/main; then undercover --compare origin/main --exclude-files " \
           "'spec/**/*,spec/*,lib/tasks/*';" \
           "fi")
  raise unless ret
end
