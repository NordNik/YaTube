from django.contrib.auth import get_user_model
from http import HTTPStatus
from django.test import TestCase, Client
from posts.models import Post, Group
from django.urls import reverse


User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(title='First_group',
                                         description='test_descript',
                                         slug='first_slug')
        cls.post = Post.objects.create(text='Test text',
                                       author=cls.user,
                                       group=cls.group)
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.pages_names = (('posts/index.html', '/'),
                           ('posts/group_list.html', '/group/first_slug/'),
                           ('posts/profile.html', '/profile/Author/'),
                           ('posts/post_detail.html', '/posts/1/'),
                           ('posts/create_post.html', '/posts/1/edit/'))

    def test_urls_correct_response(self):
        '''Check if all pages give a response'''
        for _, address in self.pages_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexist_url(self):
        '''Check if unexisting page give 404 error'''
        response = self.authorized_client.get('/posts/unexisting/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_guest_post_create(self):
        """Гостя перенаправляют на страницу входа"""
        response = self.guest_client.get('/create/')
        login_url = reverse('users:login')
        address = reverse('posts:post_create')
        self.assertRedirects(response, f'{login_url}?next={address}')

    def test_urls_uses_correct_template(self):
        '''URL-адрес использует соответствующий шаблон.'''
        for template, address in self.pages_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_url_redirect_edit_post(self):
        '''Check if author only can edit page '''
        not_author = User.objects.create_user(username='NotAuthor')
        self.not_author_client = Client()
        self.not_author_client.force_login(not_author)
        response = self.not_author_client.get('/posts/1/edit/')
        self.assertRedirects(response, '/posts/1/')
