#!/usr/bin/env python
import smash as s
import cache as c
f = c.rcache.get('smash_collect')
if not f:
    c.rcache.set('smash_collect', '1')
s.random_collect(0)
if not f:
    c.rcache.set('smash_collect','')
