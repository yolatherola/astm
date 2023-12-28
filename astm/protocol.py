# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Alexander Shorin
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#

import logging
from .asynclib import AsyncChat, call_later
from .records import HeaderRecord, TerminatorRecord
from .constants import STX,  ENQ, ACK, NAK, EOT, ENCODING

log = logging.getLogger(__name__)

__all__ = ['ASTMProtocol']


class ASTMProtocol(AsyncChat):
    """Common ASTM protocol routines."""

    #: ASTM header record class.
    astm_header = HeaderRecord
    #: ASTM terminator record class.
    astm_terminator = TerminatorRecord
    #: Flag about chunked transfer.
    is_chunked_transfer = None
    #: IO timer
    timer = None

    encoding = ENCODING
    strip_terminator = False
    _last_recv_data = None
    _last_sent_data = None

    def __init__(self, sock=None, map=None, timeout=None):
        super(ASTMProtocol, self).__init__(sock, map)
        self.buffer_message_begining = None
        self.buffer_message_ending = None
        self.buffer = None
        if timeout is not None:
            self.timer = call_later(timeout, self.on_timeout)

    def found_terminator(self):
        while self.inbox:
            data = self.inbox.popleft()
            if not data:
                continue
            self.dispatch(data)

    def dispatch(self, data):
        x17 = False
        x02 = False
        specific_ip = '192.168.1.52'
        """Dispatcher of received data."""
        if data.startswith(b'\x02') and len(data) == 2 or len(data) == 1:
            self.buffer_message_begining = data
        if data.startswith(b'\x17'):
            self.buffer_message_ending = data
            Previous_message_WITHOUTx17 = self._last_recv_data
        self._last_recv_data = data
        if data == ENQ:
            handler = self.on_enq
        elif data == ACK:
            handler = self.on_ack
        elif data == NAK:
            handler = self.on_nak
        elif data == EOT:
            handler = self.on_eot
        elif self.client_info['host'] == specific_ip:
            #protocol = Protocol(ip)
            if data.startswith(b'\x02') and len(data) == 2 or len(data) == 1:
                print("отдельное начало, запомнить к следующему")
                self.buffer = data

                print("data", data, sep=' ')
                print("buffer:", self.buffer, sep=' ')
                return
            if b'\x02' in data and not b'\x17' in data and not b'\x03' in data:

                print("начало x02, середина полная, концовки нет")
                self.buffer = data
                print("пропуск, ожидаем след. сообщение с концовкой")
                print("data", data, sep=' ')
                print("buffer:", self.buffer, sep=' ')
                return
            if (data.startswith(b'H|') or data.startswith(b'P|') or data.startswith(
                    b'O|') or data.startswith(b'R|') or data.startswith(b'L|') or data.startswith(
                b'Q|')) and b'\x17' in data:

                print("нет начала, есть x17 вконце")
                print("data", data, sep=' ')
                print("buffer:", self.buffer, sep=' ')
                self.buffer = self.buffer + data

                print("=====")
            elif (data.startswith(b'H|') or data.startswith(b'P|') or data.startswith(
                    b'O|') or data.startswith(b'R|') or data.startswith(b'L|') or data.startswith(
                b'Q|')) and not b'\x17' in data:
                print("нет начала, нет x17 вконце! Суммируем сюда следующее сообщение")
                print("data", data, sep=' ')
                print("buffer:", self.buffer, sep=' ')
                self.buffer =self.buffer + data
                print("buffer(после сложения):", self.buffer, sep=' ')
                if not b'\x03' in self.buffer:
                    return
            if data.startswith(b'\x17'):
                print("начинается с x17, прибавить к предыдущему")
                self.buffer = self.buffer + data
                print(self.buffer)
                print("data", data, sep=' ')
                print("buffer:", self.buffer, sep=' ')
            if data.startswith(b'\x03'):
                self.buffer += data
                print("03 в начале, прибавить к пред")
                # handler = self.on_message
        # elif data.startswith(b'\x02') and len(data) == 2 or len(data) == 1: #если пришло x17 или около того
        #   self.buffer_message_ending= data

            if self.buffer != None:
                print("готовое сообщение: ", self.buffer, sep=' ')
                self._last_recv_data = self.buffer
            else:
                self._last_recv_data= data
            self.buffer = None
            handler = self.on_message
        elif data.startswith(STX): # this looks like a message (стандартная обработка)
            handler = self.on_message
        else:
            handler = lambda: self.default_handler(data)  #это вызывается, потому что приходит раздельные сообщения b'\x021'
            #handler = self.on_nak

        x17 = False
        x02 = False
        resp = handler()


        if resp is not None:
            self.push(resp)

    def default_handler(self, data):
        raise ValueError('Unable to dispatch data: %r'%data)

    def push(self, data):
        self._last_sent_data = data
        if self.timer is not None and not self.timer.cancelled:
            self.timer.reset()
        return super(ASTMProtocol, self).push(data)

    def on_enq(self):
        """Calls on <ENQ> message receiving."""

    def on_ack(self):
        """Calls on <ACK> message receiving."""

    def on_nak(self):
        """Calls on <NAK> message receiving."""

    def on_eot(self):
        """Calls on <EOT> message receiving."""

    def on_message(self):
        """Calls on ASTM message receiving."""

    def on_timeout(self):
        """Calls when timeout event occurs. Used to limit waiting time for
        response data."""
        log.warning('Communication timeout')

    def handle_read(self):
        if self.timer is not None and not self.timer.cancelled:
            self.timer.reset()
        super(ASTMProtocol, self).handle_read()

    def handle_close(self):
        if self.timer is not None and not self.timer.cancelled:
            self.timer.cancel()
        super(ASTMProtocol, self).handle_close()
