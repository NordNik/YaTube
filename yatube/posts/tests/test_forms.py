from django.test import Client, TestCase
from posts.models import Post, Group

from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(title='First_group',
                                         description='test_descript',
                                         slug='first_slug')

    def setUp(self):
        self.user = User.objects.create_user(username='Author')
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

    # тест повторяет тест из урлов
    def test_guest_post_create(self):
        """Гостя перенаправляют на страницу входа"""
        self.guest_client = Client()
        response = self.guest_client.get(
            reverse('posts:post_create'),
        )
        login_url = reverse('users:login')
        address = reverse('posts:post_create')
        self.assertRedirects(response, f'{login_url}?next={address}')

    def test_author_post_create(self):
        """Валидная форма создает запись в Post."""
        form_data = {
            'text': 'Test text',
            'group': 1,
        }
        response = self.auth_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.all()[0]
        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs={'username': 'Author'}))
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(post.text, 'Test text')
        self.assertEqual(post.group.slug, 'first_slug')
        self.assertEqual(post.author.username, 'Author')
