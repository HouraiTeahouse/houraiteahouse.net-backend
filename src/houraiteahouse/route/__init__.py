from houraiteahouse.route.auth_route import auth
from houraiteahouse.route.news_route import news
from houraiteahouse.route.news_route import news
from houraiteahouse.route.errors import install_error_handlers


blueprints = {
    '/auth': auth,
    '/news': news,
}

post_process_steps = [install_error_handlers]
