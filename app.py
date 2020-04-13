#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: le4f.net
from server import app

if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8081, debug=True)
