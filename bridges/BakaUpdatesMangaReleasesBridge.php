<?php

class MastodonHomefeedBridge extends BridgeAbstract
{
    const NAME = 'Mastodon Homefeed';
    const URI = 'https://joinmastodon.org';
    const DESCRIPTION = 'Turns your mastodon homefeed into RSS';
    const MAINTAINER = 'KamaleiZestri';
    const PARAMETERS = [[
        'instance' => [
            'name' => 'Instance',
            'type' => 'text',
            'required' => true,
            'exampleValue' => 'mastodon.social'
        ],
        'accesstoken' => [
            'name' => 'Access Token',
            'required' => true
        ],
        'noava' => [
            'name' => 'Hide avatar',
            'type' => 'checkbox',
            'title' => 'Check to hide user avatars.'
        ],
        'norep' => [
            'name' => 'Without replies',
            'type' => 'checkbox',
            'title' => 'Hide replies, as determined by relations (not mentions).'
			],
        'noboost' => [
            'name' => 'Without boosts/reblogs',
            'type' => 'checkbox',
            'title' => 'Hide boosts. This will reduce loading time as RSS-Bridge fetches the boosted status from other federated instances.'
        ],
        'image' => [
            'name' => 'Select image type',
            'type' => 'list',
            'title' => 'Decides how the image is displayed, if at all.',
            'values' => [
                'None' => 'None',
                'Small' => 'Small',
                'Full' => 'Full'
            ],
            'defaultValue' => 'Full'
        ]
    ]];

    public function getURI()
    {
        return 'https://' . $this->getInput('instance') . '/home';
    }

    /**
     * Mastodon Bridge alt.
     *
     * Inherits alot from Pillowfort bridge.
     */
    public function collectData()
    {
        $header = ['Authorization: Bearer ' . $this->getInput('accesstoken')];
		$url = 'https://' . $this->getInput('instance') . '/api/v1/timelines/home';
		$content = json_decode(getContents($url, $header), true);

        $posts = $content;

        foreach ($posts as $post) {
            $item = $this->getItemFromPost($post);

            // empty when noreblogs or noreplies comes into effect
            if (!empty($item)) {
                $this->items[] = $item;
            }
        }
    }

    protected function getItemFromPost($post)
    {
        //check for reply
        if ($this -> getInput('norep') && !$post['in_reply_to_id"'] != null)
            return [];

        //check for reblog
        if ($post['reblog'] == null) {
            $embPost = false;
        } else {
            $embPost = true;
        }
        
        if ($this -> getInput('noboost') && $embPost) {
            return [];
        }

        $item = [];

        //incase of reblog, just get data from internal, original post
        if ($embPost) {
            $post = $post['reblog'];
        }


        $item['uid'] = $post['id'];
        $item['timestamp'] = strtotime($post['created_at']);
        $item['uri'] = $post['uri'];
        $item['author'] = $post['account']['username'];
        if ($post['content'] == null) {
            $item['title'] = '[NO TITLE]';
        }
        else {
            $item['title'] = $post['content'];
        }

        $avatarText = $this -> genAvatarText(
            $item['author'],
            $post['account']['avatar'],
            $post['account']['url']
        );

        $imagesText = $this -> genImagesText($post['media_attachments']);

        $item['content'] = <<<EOD
            <div style="display: inline-block; vertical-align: top;">
                {$avatarText}
            </div>
            <div style="display: inline-block; vertical-align: top;">
                {$post['content']}
            </div>
            <div style="display: block; vertical-align: top;">
                {$imagesText}
            </div>
            EOD;

        return $item;
    }

    protected function genAvatarText($author, $avatar_url, $title)
    {
        $noava = $this -> getInput('noava');

        if ($noava) {
            return '';
        } else {
            return <<<EOD
                <a href="https://{$this->getInput('instance')}/@{$author}">
                <img
                    style="align:top; width:75px; border:1px solid black;"
                    alt="{$author}"
                    src="{$avatar_url}"
                    title="{$title}" />
                </a>
                EOD;
        }
    }

    protected function genImagesText($media)
    {
        $dimensions = $this -> getInput('image');
        $text = '';

        //preg_replace used for images with spaces in the url

        if ($dimensions == 'None') {
            foreach ($media as $image) {
                $imageURL = preg_replace('[ ]', '%20', $image['url']);
                $text .= <<<EOD
                    <a href="{$imageURL}">
                    {$imageURL}
                    </a>
                    EOD;
            }
        }
        else {
            foreach ($media as $image) {
                if ($dimensions == 'Small') {
                    $imageURL = preg_replace('[ ]', '%20', $image['preview_url']);
                }
                else {
                    $imageURL = preg_replace('[ ]', '%20', $image['url']);
                }

                if (strcmp($image['type'], 'gifv') == 0) {
                    $text .= <<<EOD
                        <a href="{$imageURL}">
                            <video autoplay muted loop
                                style="align:top; max-width:558px; border:1px solid black;"
                                src="{$imageURL}" 
                            />
                        </a>
                        EOD;
                }
                else {
                    $text .= <<<EOD
                        <a href="{$imageURL}">
                            <img
                                style="align:top; max-width:558px; border:1px solid black;"
                                src="{$imageURL}" 
                            />
                        </a>
                        EOD;
                }
            }
        }

        return $text;
    }
}
