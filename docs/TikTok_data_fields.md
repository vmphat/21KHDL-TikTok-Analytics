# ------------------ `VIDEO API` ------------------

- id
- desc: caption + hashtag
- createTime
- video: height, width, duration, ratio, format, videoQuality, definition, volumeInfo, claInfo (hasOriginalAudio, enableAutoCaption, captionInfos, noCaptionReason)
- author: id, uniqueId, nickname, signature, createTime, verified
- music: id, title, duration, original, isCopyrighted
- challenges: id, title, desc (_thông tin chi tiết hơn về các hashtag_)
- stats: diggCount, shareCount, commentCount, playCount, collectCount
- statsV2: là stats nhưng thêm "repostCount"
- textExtra (_cũng liên quan đến hashtag_)
- authorStats
- shareEnabled
- isAd
- diversificationLabels (_các label của video, có thể dùng để phân loại_)
- locationCreated
- suggestedWords (_có thể là các keyword để search_)
- contents (_liên quan đến caption_)
- anchors (_liên quan tới capcut_)
- item_control: can_share, can_comment, can_music_redirect, can_creator_redirect, can_repost
- keywordTags (_có thể liên quan tới search, phân loại video, từ khoá được search nhiều nhất bởi viewer_)
- textLanguage
- textTranslatable

# ------------------ `USER API` ------------------

- id
- uniqueId
- nickname
- signature (bio)
- createTime
- verified
- ttSeller
- region
- profileTab
- followingVisibility
- nickNameModifyTime
- language
- followerCount
- followingCount
- heart
- heartCount
- videoCount
- diggCount
- friendCount
- isOrganization
- commerceUserInfo
