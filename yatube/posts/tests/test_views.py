import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.core.cache import cache
from posts.models import Post, Group, Comment, Follow
from posts.forms import PostForm, CommentForm
from django import forms
from django.conf import settings


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Author')
        cls.author_2 = User.objects.create_user(username='Author_2')
        cls.first_group = Group.objects.create(title='first group',
                                               description='test_description',
                                               slug='first_slug')
        cls.image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='image.gif',
            content=cls.image,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(text='Author_First',
                                       author=cls.author,
                                       group=cls.first_group,
                                       image=uploaded)
        cls.public_pages_names = (
            ('posts/index.html', reverse('posts:index')),
            ('posts/group_list.html',
             reverse('posts:group_list', kwargs={'slug': 'first_slug'})),
            ('posts/profile.html',
             reverse('posts:profile', kwargs={'username': 'Author'})),
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.author_2_client = Client()
        self.author_2_client.force_login(self.author_2)

    def test_public_templates(self):
        """
        Тест совпадения адреса и шаблона страниц index,
        group_list, profile
        """
        for template, reverse_name in self.public_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_other_template(self):
        """
        Тест совпадения адреса и шаблона страниц post_detail,
        post_create, post_edit
        """
        other_pages_names = (
            ('posts/post_detail.html',
             reverse('posts:post_detail', kwargs={'post_id': '1'})),
            ('posts/create_post.html', reverse('posts:post_create')),
            ('posts/create_post.html',
             reverse('posts:post_edit', kwargs={'post_id': '1'}))
        )
        for template, reverse_name in other_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_public_pages_paginator(self):
        """
        Тест паджинатора на страницах index, group_list, profile
        """
        # create 15 posts
        posts = [
            Post(text=f'Author_First_{num}',
                 author=self.author,
                 group=self.first_group) for num in range(15)
        ]
        Post.objects.bulk_create(posts)
        for _, reverse_name in self.public_pages_names:
            with self.subTest(reverse_name=reverse_name):
                resp_1page = self.author_client.get(reverse_name)
                resp_2page = self.author_client.get(reverse_name + '?page=2')
                self.assertEqual(len(resp_1page.context['page_obj']), 10)
                self.assertEqual(len(resp_2page.context['page_obj']), 6)

    def test_context_public_pages(self):
        """
        Test context on public pages
        """
        for _, reverse_name in self.public_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                post = response.context['page_obj'][0]
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.image, self.post.image)

    def test_post_detail_context(self):
        """
        Тест контекста post_detail
        """
        response = self.author_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'})
        )
        post = response.context['post']
        self.assertEqual(post.author.username, 'Author')
        self.assertEqual(post.text, 'Author_First')

    def test_post_create_context(self):
        """
        Тест контекста post_create
        """
        form_fields = (
            ('text', forms.fields.CharField),
            ('group', forms.fields.ChoiceField),
        )
        response = self.author_client.get(reverse('posts:post_create'))
        form_type = response.context.get('form')
        self.assertIsInstance(form_type, PostForm)
        for value, expected in form_fields:
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_image_context(self):
        """
        Тест сохранения в базе записи после post_create
        """
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='image.gif',
            content=self.image,
            content_type='image/gif'
        )
        form = {
            'text': 'Author_First_Image_Test',
            'group': self.first_group.id,
            'image': uploaded,
        }
        self.author_client.post(
            reverse('posts:post_create'),
            data=form,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_post_edit_context(self):
        """
        Тест контекста post_edit
        """
        form_fields = (
            ('text', forms.fields.CharField),
            ('group', forms.fields.ChoiceField),
        )
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'})
        )
        form_type = response.context.get('form')
        self.assertIsInstance(form_type, PostForm)
        for value, expected in form_fields:
            with self.subTest(value=value):
                self.assertTrue(response.context[0]['is_edit'], bool)
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    # Comments tests
    def test_comment_guest_not_allowed(self):
        """
        Guest is redirected to login page
        """
        response = self.guest_client.get(
            reverse('posts:add_comment', kwargs={'post_id': '1'})
        )
        login_url = reverse('users:login')
        address = reverse('posts:add_comment', kwargs={'post_id': 1})
        self.assertRedirects(response, f'{login_url}?next={address}')

    def test_comment_form(self):
        """
        Tests fields of CommentForm at post_detail
        """
        form_fields = (
            ('text', forms.fields.CharField),
        )
        response = self.author_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': 1}
            )
        )
        form_type = response.context.get('form')
        self.assertIsInstance(form_type, CommentForm)
        for value, expected in form_fields:
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_comment_saving(self):
        """
        Test if new comment appears in database
        """
        form = {'text': 'Comment_Test', }
        self.author_client.post(
            reverse('posts:add_comment', kwargs={'post_id': 1}),
            data=form,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), 1)

    # Cache tests
    def test_cache_page(self):
        """
        Cache test
        """
        response = self.author_client.get(reverse('posts:index'))
        content_before = response.content
        self.post = Post.objects.create(
            text='Author_First_cache',
            author=self.author,
            group=self.first_group
        )
        response = self.author_client.get(reverse('posts:index'))
        content_after = response.content
        cache.clear()
        response = self.author_client.get(reverse('posts:index'))
        content_clean_cache = response.content
        self.assertEqual(content_before, content_after)
        self.assertNotEqual(content_before, content_clean_cache)

    # Subscriptions tests
    def test_user_is_able_to_subscribe(self):
        """
        User can subscribe to author
        """
        self.author_client.get(
            reverse('posts:profile_follow', kwargs={'username': 'Author_2'})
        )
        self.assertEqual(Follow.objects.count(), 1)

    def test_user_is_able_to_unsubscribe(self):
        """
        User can unsubscribe to author
        """
        self.author_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': 'Author_2'})
        )
        self.assertEqual(Follow.objects.count(), 0)

    def test_new_post_for_followers(self):
        """
        Tests if follower sees author post but others don't
        """
        self.author_client.get(
            reverse('posts:profile_follow', kwargs={'username': 'Author_2'})
        )
        post_author_2 = Post.objects.create(
            text='Test',
            author=self.author_2,
            group=self.first_group,
        )
        response = self.author_client.get(reverse('posts:follow_index'))
        post = response.context['page_obj'][0]
        self.assertEqual(post.author, post_author_2.author)
        self.author_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': 'Author_2'})
        )
        response = self.author_2_client.get(reverse('posts:follow_index'))
        post = response.context['page_obj']
        self.assertFalse(post)
