def configure(app):
    app.config.update(
        DEBUG=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///test.db',
        SECRET_KEY='3nc0aj14o4-zlfm2k=-1n290zp-42nlz9s0jzxlk4'
    )
