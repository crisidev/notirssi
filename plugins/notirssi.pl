##
## Put me in ~/.irssi/scripts, and then execute the following in irssi:
##
##       /load perl
##       /script load notirssi
##

use strict;
use Irssi;
use vars qw($VERSION %IRSSI);
use IO::Socket;

$VERSION = "1.0";
%IRSSI = (
    idea        => 'Bernard `Guyzmo` Pratz, Luke Macken, Paul W. Frields - http://github.com/guyzmo/notossh',
    authors     => 'Matteo Bigoi',
    contact     => 'bigo at crisidev dot org',
    name        => 'notirssi.pl',
    description => 'Use libnotify / osx notification / growl / dbus over SSH to alert user for hilighted messages',
    license     => 'WTF Public License <http://sam.zoy.org/wtfpl/>',
    url         => 'http://github.com/crisidev/notirssi',
);

sub notify {
    my ($server, $summary, $message) = @_;
    my $separator = "|x|";

    my $remote = IO::Socket::INET->new(
                        reuse    => 1,
                        Proto    => "tcp",
                        PeerAddr => Irssi::settings_get_str('notirssi_host'),
                        PeerPort => Irssi::settings_get_int('notirssi_port'),
                    )
                  or do {
			print("notirssi.pl: cannot connect to notification daemon: $!");
			return;
			};
    # ... write notifications to the socket ... #
	  print $remote $summary . $separator . $message . "\n";
}

sub print_text_notify {
    my ($dest, $text, $message) = @_;
    my $server = $dest->{server};

    return if (!$server || !($dest->{level} & MSGLEVEL_HILIGHT));
    my $clean_message = $message;
    $clean_message =~ s/^\<.([^\>]+)\>.+/\1/ ;
    my $sender = (split(/\|/, $clean_message))[0];
    $sender =~ s/^\@// ;
    my $nick = $sender . "@" . $dest->{target};

    $message =~ s/^\<.[^\>]+\>.// ;
    $message =~ s/^\@// ;
    $message = (split(/\|/, $message))[1];
    notify($server, $nick, $message);
}

sub message_private_notify {
    my ($server, $msg, $nick, $address) = @_;

    return if (!$server);
    notify($server, $nick, $msg);
}

sub dcc_request_notify {
    my ($dcc, $sendaddr) = @_;
    my $server = $dcc->{server};

    return if (!$dcc);
    my $nick = "DDC ". $dcc->{nick};
    my $message = "DCC ". $dcc->{type} . "request";
    notify($server, $nick, $message);
}

# Register settings
Irssi::settings_add_int('misc', 'notirssi_port', 4223);
Irssi::settings_add_str('misc', 'notirssi_host', 'localhost');

# Register signals
Irssi::signal_add('print text', 'print_text_notify');
Irssi::signal_add('message private', 'message_private_notify');
Irssi::signal_add('dcc request', 'dcc_request_notify');
