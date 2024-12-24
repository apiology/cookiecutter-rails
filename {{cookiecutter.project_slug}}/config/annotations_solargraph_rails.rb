# The following comments fill some of the gaps in Solargraph's understanding of
# Rails apps. Since they're all in YARD, they get mapped in Solargraph but
# ignored at runtime.
#
# You can put this file anywhere in the project, as long as it gets included in
# the workspace maps. It's recommended that you keep it in a standalone file
# instead of pasting it into an existing one.
#
# @!parse
#   module AbstractController
#     module Callbacks
#       module ClassMethods
#         # @param names [Array<Symbol>]
#         # @return [void]
#         def before_action(*names, &block); end
#         # @param names [Array<Symbol>]
#         # @return [void]
#         def prepend_before_action(*names, &block); end
#         # @param names [Array<Symbol>]
#         # @return [void]
#         def skip_before_action(*names, &block); end
#         # @param names [Array<Symbol>]
#         # @return [void]
#         def around_action(*names, &block); end
#       end
#     end
#   end
#   class ActionController::Base
#     include ActionController::MimeResponds
#     include ActionController::Redirecting
#     include ActionController::Cookies
#     include AbstractController::Rendering
#     extend ActiveSupport::Callbacks::ClassMethods
#     extend ActiveSupport::Rescuable::ClassMethods
#     extend ActionController::AllowBrowser::ClassMethods
#     extend AbstractController::Callbacks::ClassMethods
#     extend ActionController::RequestForgeryProtection::ClassMethods
#   end
#   class ActionController::API
#     include ActionController::MimeResponds
#     include ActionController::Base
#     include ActionController::Renderer
#     extend ActiveSupport::Callbacks::ClassMethods
#     extend AbstractController::Callbacks::ClassMethods
#   end
#   class ActionDispatch::Routing::Mapper
#     include ActionDispatch::Routing::Mapper::Base
#     include ActionDispatch::Routing::Mapper::HttpHelpers
#     include ActionDispatch::Routing::Mapper::Redirection
#     include ActionDispatch::Routing::Mapper::Scoping
#     include ActionDispatch::Routing::Mapper::Concerns
#     include ActionDispatch::Routing::Mapper::Resources
#     include ActionDispatch::Routing::Mapper::CustomUrls
#   end
#
# @!override ActionDispatch::Request#headers
#   @return [Http::Headers]
#
# @!override ActionDispatch::Http::Headers#fetch
#   @param key [String]
#   @return [String]
#
# @!parse
#   class ActionMailer::Base
#     extend ActionView::Layouts::ClassMethods
#   end
#   class Rails::Railtie
#     # @yieldself [Rails::Application]
#     # @return [void]
#     def configure(&block); end
#   end
#   module Rails
#     # @return [Rails::Application]
#     def self.application; end
#   end
#   class Rails::Application
#     # @return [ActionDispatch::Routing::RouteSet]
#     def routes; end
#     # include Rails::Railtie
#   end
#   class ActionDispatch::Routing::RouteSet
#     # @yieldself [ActionDispatch::Routing::Mapper]
#     # @return [void]
#     def draw; end
#   end
#   class ActiveJob::Base
#     extend ActiveJob::Core::ClassMethods
#     extend ActiveJob::QueueName::ClassMethods
#     extend ActiveJob::Enqueuing::ClassMethods
#   end
#   class ActiveRecord::Base
#     extend ActiveModel::Validations::ClassMethods
#     extend ActiveRecord::Encryption::EncryptableRecord
#     extend ActiveRecord::QueryMethods
#     extend ActiveRecord::FinderMethods
#     extend ActiveRecord::Associations::ClassMethods
#     extend ActiveRecord::Inheritance::ClassMethods
#     extend ActiveRecord::Scoping::Named::ClassMethods
#     extend ActiveRecord::Callbacks::ClassMethods
#     extend ActiveRecord::Relation
#     include ActiveRecord::AttributeMethods::PrimaryKey
#     include ActiveRecord::Persistence
#   end
#
# @!override ActiveRecord::QueryMethods#where
#   @return [ActiveRecord::Relation]
#
# @!parse
#   class ActiveRecord::Relation
#     # @see ActiveRecord::Result#each
#     # @return [void]
#     def each(&block); end
#   end
