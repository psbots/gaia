# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import time

from marionette import SkipTest

from gaiatest import GaiaTestCase
from gaiatest.apps.email.app import Email


class TestSendIMAPEmail(GaiaTestCase):

    def setUp(self):
        try:
            account = self.testvars['email']['IMAP']
        except KeyError:
            raise SkipTest('account details not present in test variables')

        GaiaTestCase.setUp(self)
        self.connect_to_network()

        self.email = Email(self.marionette)
        self.email.launch()

        # setup IMAP account
        self.email.setup_IMAP_email(account)

    def test_send_imap_email(self):
        # Bug 878772 - email app doesn't show the last emails by default
        self.email.wait_for_emails_to_sync()
        self.email.mails[0].scroll_to_message()

        curr_time = repr(time.time()).replace('.', '')
        _subject = 's%s' % curr_time
        _body = 'b%s' % curr_time
        new_email = self.email.header.tap_compose()

        new_email.type_to(self.testvars['email']['IMAP']['email'])
        new_email.type_subject(_subject)
        new_email.type_body(_body)

        self.email = new_email.tap_send()

        # wait for the email to be sent before we tap refresh
        self.email.wait_for_email(_subject)

        # assert that the email app subject is in the email list
        self.assertIn(_subject, [mail.subject for mail in self.email.mails])

        read_email = self.email.mails[0].tap_subject()

        self.assertEqual(_body, read_email.body)
        self.assertEqual(_subject, read_email.subject)
